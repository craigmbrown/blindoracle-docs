"""Stub coinbase_agentkit so tests run without installing the real package."""
import sys
import types


def _create_action(**kwargs):
    def decorator(fn):
        fn._agentkit_action = kwargs
        return fn
    return decorator


class _ActionProvider:
    def __init__(self, name, networks):
        self.name = name

    def __class_getitem__(cls, item):
        return cls


class _Network:
    def __init__(self, network_id=None):
        self.network_id = network_id


class _WalletProvider:
    pass


def _make(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


_coinbase = _make("coinbase_agentkit")
_ap      = _make("coinbase_agentkit.action_providers")
_ad      = _make("coinbase_agentkit.action_providers.action_decorator")
_aprov   = _make("coinbase_agentkit.action_providers.action_provider")
_net     = _make("coinbase_agentkit.network")
_wp      = _make("coinbase_agentkit.wallet_providers")

_ad.create_action          = _create_action
_aprov.ActionProvider      = _ActionProvider
_net.Network               = _Network
_wp.WalletProvider         = _WalletProvider
_coinbase.action_providers = _ap
_ap.action_decorator       = _ad
_ap.action_provider        = _aprov
_coinbase.network          = _net
_coinbase.wallet_providers = _wp
