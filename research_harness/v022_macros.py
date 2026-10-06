"""Controller-only macros for the observed exact-v0.22 menus.

Call only on an owned disposable session at the named starting screen.
These sequences are observations, not generic emulator navigation. Persistence
must still be independently audited after process shutdown and cold reload.
"""


def settle(client, groups=2):
    for _ in range(groups):
        client.command('frames', 120)


def tap(client, key):
    client.command('set_keys', key)
    client.command('frames', 6)
    client.command('set_keys', 0)
    settle(client)


def boot_continue(client):
    """Observed stable title -> Continue -> field; no SAVE or RAM writes.

    The caller first waits for and confirms the title screen. Opening-animation
    RAM may already contain save records and is not a readiness predicate.
    """
    tap(client, 8)
    tap(client, 8)  # skip remaining title transition and reach Continue
    tap(client, 1)  # retained Continue choice
    settle(client)


def normal_report(client):
    """Field with default top-left menu cursor -> Report -> two Yes prompts.

    Preconditions: observed menu, existing disposable save, no open dialogue,
    freshly opened default menu cursor. Returning directly from Bag to the
    open menu differs: close that menu before starting this macro.
    The caller checks RAM before and returned save
    afterward; the macro alone is never persistence evidence.
    """
    tap(client, 8)
    for _ in range(2):
        tap(client, 128)
    tap(client, 1)
    tap(client, 1)
    tap(client, 1)
    settle(client, 5)


def open_shop_buy_list(client):
    """Clerk-facing field -> A -> top Buy choice A -> sales list.

    Operator-described sequence, reproduced on the owned disposable session.
    This does not choose an item or confirm a purchase.
    """
    tap(client, 1)
    tap(client, 1)
