use crate::enrichment::SwapEnricher;
use crate::error::parse_address;
use crate::schema::SwapEvent;
use crate::service::DextradesService;
use async_trait::async_trait;
use eyre::Result;
use serde_json;

/// Enricher that adds token metadata (addresses, symbols, decimals)
pub struct TokenMetadataEnricher;

#[async_trait]
impl SwapEnricher for TokenMetadataEnricher {
    fn name(&self) -> &'static str {
        "token_metadata"
    }

    fn required_fields(&self) -> Vec<&'static str> {
        vec!["pool_address", "dex_protocol"]
    }

    fn provided_fields(&self) -> Vec<&'static str> {
        vec![
            "token0_address",
            "token1_address",
            "token0_symbol",
            "token1_symbol",
            "token0_decimals",
            "token1_decimals",
        ]
    }

    async fn enrich(&self, events: &mut [SwapEvent], service: &DextradesService) -> Result<()> {
        use log::{debug, info};
        use std::collections::{HashMap, HashSet};
        use alloy::primitives::Address;
        
        if events.is_empty() {
            return Ok(());
        }

        info!("🚀 [TokenMetadataEnricher] Starting enrichment for {} events", events.len());
        let start_time = std::time::Instant::now();

        // First pass: collect all unique pool addresses and get their tokens in parallel
        let mut pool_addresses_to_fetch: Vec<(String, String)> = Vec::new();
        
        for event in events.iter() {
            pool_addresses_to_fetch.push((event.pool_address.clone(), event.dex_protocol.clone()));
        }
        
        // Remove duplicates
        pool_addresses_to_fetch.sort_unstable();
        pool_addresses_to_fetch.dedup();
        
        info!("📋 [TokenMetadataEnricher] Found {} unique pools to process", pool_addresses_to_fetch.len());

        // Process pools in very small batches to avoid overwhelming RPC providers (global parallel chunks)
        // Using 1 here materially reduces cross-chunk RPC fan-out while maintaining correctness
        let max_concurrent_pools = 1;
        let mut pool_tokens_map: HashMap<String, Option<(Address, Address)>> = HashMap::new();
        
        for pool_batch in pool_addresses_to_fetch.chunks(max_concurrent_pools) {
            info!("🔄 [TokenMetadataEnricher] Processing batch of {} pools (max concurrent: {})", pool_batch.len(), max_concurrent_pools);
            
            // Fetch pool tokens in parallel for this batch
            let pool_token_futures: Vec<_> = pool_batch
                .iter()
                .map(|(pool_address, dex_protocol)| {
                    let service = service.clone();
                    let pool_address = pool_address.clone();
                    let dex_protocol = dex_protocol.clone();
                    async move {
                        let pool_tokens_result = match dex_protocol.as_str() {
                            "uniswap_v2" => match parse_address(&pool_address) {
                                Ok(pool_addr) => {
                                    match crate::protocols::uniswap_v2::get_pool_tokens(
                                        service.rpc_service(),
                                        pool_addr,
                                    ).await {
                                        Ok(tokens) => Some(tokens),
                                        Err(e) => {
                                            debug!("Failed to get V2 pool tokens for {}: {}", pool_addr, e);
                                            None
                                        }
                                    }
                                },
                                Err(e) => {
                                    debug!("Invalid pool address for V2: {}", e);
                                    None
                                }
                            },
                            "uniswap_v3" => match parse_address(&pool_address) {
                                Ok(pool_addr) => {
                                    match crate::protocols::uniswap_v3::get_pool_tokens(
                                        service.rpc_service(),
                                        pool_addr,
                                    ).await {
                                        Ok(tokens) => Some(tokens),
                                        Err(e) => {
                                            debug!("Failed to get V3 pool tokens for {}: {}", pool_addr, e);
                                            None
                                        }
                                    }
                                },
                                Err(e) => {
                                    debug!("Invalid pool address for V3: {}", e);
                                    None
                                }
                            },
                            _ => {
                                log::warn!("Unknown protocol for token metadata: {}", dex_protocol);
                                None
                            }
                        };
                        (pool_address, pool_tokens_result)
                    }
                })
                .collect();

            // Wait for this batch of pool token results
            let pool_token_results = futures::future::join_all(pool_token_futures).await;
            
            // Add results to the main map
            for (pool_address, tokens) in pool_token_results {
                pool_tokens_map.insert(pool_address, tokens);
            }
            
            // Small delay between batches to avoid overwhelming RPC providers
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }

        // Second pass: collect all unique token addresses
        let mut unique_token_addresses = HashSet::new();
        let mut successful_pools = 0;
        let mut failed_pools = 0;
        
        for event in events.iter() {
            if let Some(Some((token0, token1))) = pool_tokens_map.get(&event.pool_address) {
                unique_token_addresses.insert(*token0);
                unique_token_addresses.insert(*token1);
                successful_pools += 1;
            } else {
                failed_pools += 1;
                debug!("❌ [TokenMetadataEnricher] No tokens found for pool: {}", event.pool_address);
            }
        }
        
        info!("🪙 [TokenMetadataEnricher] Pool token resolution: {} successful, {} failed", successful_pools, failed_pools);
        info!("🪙 [TokenMetadataEnricher] Found {} unique token addresses to enrich", unique_token_addresses.len());

        // Fetch all token metadata in bulk using the enhanced service
        let token_addresses: Vec<Address> = unique_token_addresses.into_iter().collect();
        info!("⚡ [TokenMetadataEnricher] Starting bulk token metadata fetch for {} tokens", token_addresses.len());
        
        let token_metadata_results = if !token_addresses.is_empty() {
            use futures::stream::{self, StreamExt};
            const MAX_TOKEN_META_CONCURRENCY: usize = 8;
            let fetch_start = std::time::Instant::now();
            let results: Vec<(Address, Result<Option<crate::service::TokenInfo>, crate::error::DextradesError>)> = stream::iter(token_addresses.iter().cloned())
                .map(|addr| {
                    let svc = service.clone();
                    async move {
                        let addr_str = addr.to_string();
                        let res = svc.get_token_metadata(&addr_str).await;
                        (addr, res)
                    }
                })
                .buffer_unordered(MAX_TOKEN_META_CONCURRENCY)
                .collect()
                .await;
            let fetch_duration = fetch_start.elapsed();
            info!("⚡ [TokenMetadataEnricher] Fetched {} tokens in {:?} with bounded concurrency {}", results.len(), fetch_duration, MAX_TOKEN_META_CONCURRENCY);
            results
        } else {
            Vec::new()
        };

        // Build token metadata map
        let mut token_metadata_map = HashMap::new();
        let mut successful_fetches = 0;
        let mut failed_fetches = 0;
        
        for (addr, result) in token_metadata_results {
            match result {
                Ok(Some(token_info)) => {
                    token_metadata_map.insert(addr, token_info);
                    successful_fetches += 1;
                }
                Ok(None) => {
                    debug!("❌ [TokenMetadataEnricher] No metadata found for token: {}", addr);
                    failed_fetches += 1;
                }
                Err(e) => {
                    debug!("❌ [TokenMetadataEnricher] Error fetching metadata for token {}: {}", addr, e);
                    failed_fetches += 1;
                }
            }
        }
        
        info!("📊 [TokenMetadataEnricher] Token metadata fetch results: {} successful, {} failed", successful_fetches, failed_fetches);

        // Third pass: enrich all events with the collected data
        let mut enriched_events = 0;
        for event in events.iter_mut() {
            if let Some(Some((token0, token1))) = pool_tokens_map.get(&event.pool_address) {
                // Add token addresses
                let token0_str = token0.to_string();
                let token1_str = token1.to_string();

                event.add_enriched_field(
                    "token0_address".to_string(),
                    serde_json::Value::String(token0_str.clone()),
                );
                event.add_enriched_field(
                    "token1_address".to_string(),
                    serde_json::Value::String(token1_str.clone()),
                );

                // Also populate legacy fields for backward compatibility
                event.token0_address = Some(token0_str.clone());
                event.token1_address = Some(token1_str.clone());

                // Add token0 metadata if available
                if let Some(token0_info) = token_metadata_map.get(token0) {
                    let (_, symbol, decimals) = token0_info.as_tuple();

                    event.add_enriched_field(
                        "token0_symbol".to_string(),
                        serde_json::Value::String(symbol.clone()),
                    );
                    event.add_enriched_field(
                        "token0_decimals".to_string(),
                        serde_json::Value::Number(serde_json::Number::from(decimals)),
                    );

                    // Also populate legacy fields
                    event.token0_symbol = Some(symbol.clone());
                    log::debug!("[TokenMetadata] Set token0_symbol to {} for pool {} in block {}", symbol, event.pool_address, event.block_number);
                    event.token0_decimals = Some(decimals);
                }

                // Add token1 metadata if available
                if let Some(token1_info) = token_metadata_map.get(token1) {
                    let (_, symbol, decimals) = token1_info.as_tuple();

                    event.add_enriched_field(
                        "token1_symbol".to_string(),
                        serde_json::Value::String(symbol.clone()),
                    );
                    event.add_enriched_field(
                        "token1_decimals".to_string(),
                        serde_json::Value::Number(serde_json::Number::from(decimals)),
                    );

                    // Also populate legacy fields
                    event.token1_symbol = Some(symbol.clone());
                    log::debug!("[TokenMetadata] Set token1_symbol to {} for pool {} in block {}", symbol, event.pool_address, event.block_number);
                    event.token1_decimals = Some(decimals);
                }
                
                enriched_events += 1;
            }
        }

        let duration = start_time.elapsed();
        info!("✅ [TokenMetadataEnricher] Completed enrichment for {}/{} events in {:?}", enriched_events, events.len(), duration);
        info!("📊 [TokenMetadataEnricher] Final stats - Events: {}, Pools resolved: {}, Tokens found: {}, Tokens enriched: {}/{}", 
              events.len(), successful_pools, token_addresses.len(), successful_fetches, token_addresses.len());

        Ok(())
    }
}
