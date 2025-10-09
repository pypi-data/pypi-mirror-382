import unittest.mock
import pytest

import py_randomprime


def test_patch_iso(tmp_path):
    py_randomprime.rust.patch_iso = unittest.mock.MagicMock()

    py_randomprime.patch_iso(
        tmp_path.joinpath("input.iso"),
        tmp_path.joinpath("output.iso"),
        {},
        py_randomprime.ProgressNotifier(print),
    )

    py_randomprime.rust.patch_iso.assert_called_once()


@pytest.mark.parametrize(
    "version, symbols",
    [
        (
            "0-00",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091B94,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006BC68,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80015D14,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091BF0,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091D68,
                "SetLayerActive__16CWorldLayerStateFiib": 0x802342C0,
                "StateForWorld__10CGameStateFUi": 0x801D39D8,
                "UpdateHintState__13CStateManagerFf": 0x80044D38,
                "g_GameState": 0x805A8C40,
                "g_StateManager": 0x8045A1A8,
                "wstring_l__4rstlFPCw": 0x800159F0,
            },
        ),
        (
            "0-01",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091c10,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006bce4,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80015d90,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091c6c,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091de4,
                "SetLayerActive__16CWorldLayerStateFiib": 0x8023433c,
                "StateForWorld__10CGameStateFUi": 0x801d3a54,
                "UpdateHintState__13CStateManagerFf": 0x80044db4,
                "g_GameState": 0x805a8e20,
                "g_StateManager": 0x8045a388,
                "wstring_l__4rstlFPCw": 0x80015a6c,
            },
        ),
        (
            "0-02",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80092118,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006c1ec,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80015fdc,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80092174,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x800922ec,
                "SetLayerActive__16CWorldLayerStateFiib": 0x80234b50,
                "StateForWorld__10CGameStateFUi": 0x801d4228,
                "UpdateHintState__13CStateManagerFf": 0x80045024,
                "g_GameState": 0x805a9ce0,
                "g_StateManager": 0x8045b208,
                "wstring_l__4rstlFPCw": 0x80015cb8,
            },
        ),
        (
            "kor",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091c08,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006bcdc,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80015d88,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091c64,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091ddc,
                "SetLayerActive__16CWorldLayerStateFiib": 0x80234334,
                "StateForWorld__10CGameStateFUi": 0x801d3a4c,
                "UpdateHintState__13CStateManagerFf": 0x80044dac,
                "g_GameState": 0x805a8920,
                "g_StateManager": 0x80459e88,
                "wstring_l__4rstlFPCw": 0x80015a64,
            },
        ),
        (
            "jpn",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80092de0,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006d57c,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80016920,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80092e3c,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80092fb4,
                "SetLayerActive__16CWorldLayerStateFiib": 0x80225d14,
                "StateForWorld__10CGameStateFUi": 0x801c7bf4,
                "UpdateHintState__13CStateManagerFf": 0x80046d9c,
                "g_GameState": 0x80591ce0,
                "g_StateManager": 0x80443030,
                "wstring_l__4rstlFPCw": 0x8001660c,
            },
        ),
        (
            "pal",
            {
                "DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091ef8,
                "DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo": 0x8006c79c,
                "Freeze__7CPlayerFR13CStateManagerUiUsUi": 0x80016630,
                "IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x80091f54,
                "InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei": 0x800920cc,
                "SetLayerActive__16CWorldLayerStateFiib": 0x802248bc,
                "StateForWorld__10CGameStateFUi": 0x801c67e4,
                "UpdateHintState__13CStateManagerFf": 0x80046028,
                "g_GameState": 0x8046ad44,
                "g_StateManager": 0x803e2088,
                "wstring_l__4rstlFPCw": 0x8001631c,
            },
        ),
    ],
)
def test_symbols_for_version(version, symbols):
    assert py_randomprime.symbols_for_version(version) == symbols
