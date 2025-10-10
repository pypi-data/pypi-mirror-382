from typing import Any

from aiochainscan.modules.base import BaseModule


class Transaction(BaseModule):
    """Transactions

    https://docs.etherscan.io/api-endpoints/stats
    """

    # TODO: Deprecated in next major. Prefer facades in `aiochainscan.__init__`.

    @property
    def _module(self) -> str:
        return 'transaction'

    async def contract_execution_status(self, txhash: str) -> dict[str, Any]:
        """[BETA] Check Contract Execution Status (if there was an error during contract execution)"""
        from aiochainscan.modules.base import _facade_injection, _resolve_api_context
        from aiochainscan.services.transaction import (
            get_contract_execution_status as _svc_get_status,
        )

        http, endpoint = _facade_injection(self._client)
        api_kind, network, api_key = _resolve_api_context(self._client)
        # Avoid strict TxHash for loose tests; services accept str via normalization
        return await _svc_get_status(
            txhash=txhash,  # type: ignore[arg-type]
            api_kind=api_kind,
            network=network,
            api_key=api_key,
            http=http,
            _endpoint_builder=endpoint,
        )

    async def tx_receipt_status(self, txhash: str) -> dict[str, Any]:
        """[BETA] Check Transaction Receipt Status (Only applicable for Post Byzantium fork transactions)"""
        from aiochainscan.modules.base import _facade_injection, _resolve_api_context
        from aiochainscan.services.transaction import (
            get_tx_receipt_status as _svc_tx_receipt_status,
        )

        http, endpoint = _facade_injection(self._client)
        api_kind, network, api_key = _resolve_api_context(self._client)
        # Avoid strict TxHash for loose tests; services accept str via normalization
        return await _svc_tx_receipt_status(
            txhash=txhash,  # type: ignore[arg-type]
            api_kind=api_kind,
            network=network,
            api_key=api_key,
            http=http,
            _endpoint_builder=endpoint,
        )

    async def check_tx_status(self, txhash: str) -> dict[str, Any]:
        """Check transaction receipt status.

        This is a wrapper around tx_receipt_status for better naming consistency.
        Only applicable for Post Byzantium fork transactions.

        Args:
            txhash: Transaction hash to check

        Returns:
            Dictionary containing transaction receipt status

        Example:
            ```python
            status = await client.transaction.check_tx_status('0x...')
            print(f"Status: {status}")
            ```
        """
        return await self.tx_receipt_status(txhash)

    async def get_by_hash(self, txhash: str) -> dict[str, Any]:
        """Fetch transaction by hash via facade when available."""
        from aiochainscan.modules.base import _facade_injection
        from aiochainscan.services.transaction import (
            get_transaction_by_hash as _svc_get_tx_by_hash,
        )

        http, endpoint = _facade_injection(self._client)
        from aiochainscan.domain.models import TxHash
        from aiochainscan.modules.base import _resolve_api_context

        api_kind, network, api_key = _resolve_api_context(self._client)
        return await _svc_get_tx_by_hash(
            txhash=TxHash(txhash),
            api_kind=api_kind,
            network=network,
            api_key=api_key,
            http=http,
            _endpoint_builder=endpoint,
        )
