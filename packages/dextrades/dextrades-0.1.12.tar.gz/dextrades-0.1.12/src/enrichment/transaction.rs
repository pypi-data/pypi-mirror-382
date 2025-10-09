use crate::enrichment::SwapEnricher;
use crate::schema::SwapEvent;
use crate::service::DextradesService;
use async_trait::async_trait;
use eyre::Result;
use serde_json;
use futures::stream::{self, StreamExt};

/// Enricher that adds transaction context fields
pub struct TransactionEnricher;

#[async_trait]
impl SwapEnricher for TransactionEnricher {
    fn name(&self) -> &'static str {
        "transaction"
    }

    fn required_fields(&self) -> Vec<&'static str> {
        vec!["tx_hash"]
    }

    fn provided_fields(&self) -> Vec<&'static str> {
        vec!["tx_from", "tx_to", "gas_used"]
    }

    async fn enrich(&self, events: &mut [SwapEvent], service: &DextradesService) -> Result<()> {
        const MAX_TX_CONCURRENCY: usize = 8;
        // Prepare owned tx hashes with indices to avoid lifetime issues
        let indexed_hashes: Vec<(usize, String)> = events.iter().enumerate().map(|(i, e)| (i, e.tx_hash.clone())).collect();

        // Fire bounded-concurrency requests and collect results with indices
        let results: Vec<(usize, Result<crate::service::TxDetails, crate::error::DextradesError>)> = stream::iter(indexed_hashes)
            .map(|(i, tx_hash)| {
                let svc = service.clone();
                async move { (i, svc.get_tx_details(tx_hash).await) }
            })
            .buffer_unordered(MAX_TX_CONCURRENCY)
            .collect()
            .await;

        // Apply results back onto events
        for (idx, res) in results {
            if let Ok(tx_details) = res {
                let event = &mut events[idx];
                if let Some(tx_from) = tx_details.tx_from {
                    event.add_enriched_field("tx_from".to_string(), serde_json::Value::String(tx_from.clone()));
                    event.tx_from = Some(tx_from);
                }
                if let Some(tx_to) = tx_details.tx_to {
                    event.add_enriched_field("tx_to".to_string(), serde_json::Value::String(tx_to.clone()));
                    event.tx_to = Some(tx_to);
                }
                if let Some(gas_used) = tx_details.gas_used {
                    event.add_enriched_field("gas_used".to_string(), serde_json::Value::Number(serde_json::Number::from(gas_used)));
                    event.gas_used = Some(gas_used);
                }
            } else if let Err(e) = res {
                log::warn!("Failed to get transaction details for {}: {}", events[idx].tx_hash, e);
            }
        }

        Ok(())
    }
}
