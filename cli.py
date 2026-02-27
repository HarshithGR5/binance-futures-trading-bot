#!/usr/bin/env python3
"""CLI entry-point for PrimeTrade AI."""

from __future__ import annotations

import logging

import click
from colorama import Fore, Style, init as colorama_init

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import format_order_response, place_order
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

colorama_init(autoreset=True)
setup_logging()
logger = logging.getLogger(__name__)



def _success(msg: str) -> None:
    click.echo(f"{Fore.GREEN}✔ {msg}{Style.RESET_ALL}")


def _error(msg: str) -> None:
    click.echo(f"{Fore.RED}✖ {msg}{Style.RESET_ALL}")


def _info(msg: str) -> None:
    click.echo(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")


def _print_request_summary(
    symbol: str, side: str, order_type: str, quantity, price, stop_price
) -> None:
    click.echo(f"\n{Fore.YELLOW}{'─' * 44}")
    click.echo(f"  ORDER REQUEST SUMMARY")
    click.echo(f"{'─' * 44}{Style.RESET_ALL}")
    click.echo(f"  Symbol      : {symbol}")
    click.echo(f"  Side        : {side}")
    click.echo(f"  Type        : {order_type}")
    click.echo(f"  Quantity    : {quantity}")
    click.echo(f"  Price       : {price or 'MARKET'}")
    click.echo(f"  Stop Price  : {stop_price or 'N/A'}")
    click.echo(f"{Fore.YELLOW}{'─' * 44}{Style.RESET_ALL}\n")



@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PrimeTrade AI – Binance Futures Testnet Trading Bot."""
    if ctx.invoked_subcommand is None:
        interactive_menu()


# ── Order subcommand ──────────────────────────────────────────────────

@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side", "-d", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--type", "-t", "order_type", required=True, type=click.Choice(["MARKET", "LIMIT", "STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"], case_sensitive=False), help="Order type")
@click.option("--quantity", "-q", required=True, type=float, help="Order quantity")
@click.option("--price", "-p", default=None, type=float, help="Limit price (required for LIMIT/STOP/TAKE_PROFIT)")
@click.option("--stop-price", default=None, type=float, help="Stop price (required for STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET)")
def order(symbol, side, order_type, quantity, price, stop_price):
    """Place an order on Binance Futures Testnet."""
    _execute_order(symbol, side, order_type, quantity, price, stop_price)



@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair, e.g. BTCUSDT")
def price(symbol):
    """Fetch the current price for a symbol."""
    try:
        client = BinanceClient()
        symbol = validate_symbol(symbol)
        data = client.ticker_price(symbol)
        _success(f"{data['symbol']} = {data['price']}")
    except Exception as exc:
        _error(str(exc))
        logger.exception("Price fetch failed")



@cli.command()
def account():
    """Show testnet account balances."""
    try:
        client = BinanceClient()
        info = client.account_info()
        click.echo(f"\n{Fore.CYAN}Account Balances (non-zero):{Style.RESET_ALL}")
        for asset in info.get("assets", []):
            balance = float(asset.get("walletBalance", 0))
            if balance != 0:
                click.echo(f"  {asset['asset']:>8s}  {balance:>14.4f}")
        click.echo()
    except Exception as exc:
        _error(str(exc))
        logger.exception("Account info failed")


def _execute_order(symbol, side, order_type, quantity, price, stop_price):
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        qty = validate_quantity(quantity)
        validated_price = validate_price(price, order_type)
        validated_stop = validate_stop_price(stop_price, order_type)
    except ValueError as exc:
        _error(f"Validation error: {exc}")
        logger.warning("Input validation failed: %s", exc)
        return

    _print_request_summary(symbol, side, order_type, qty, validated_price, validated_stop)

    try:
        client = BinanceClient()
        resp = place_order(
            client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=qty,
            price=validated_price,
            stop_price=validated_stop,
        )
        click.echo(format_order_response(resp))
        _success("Order placed successfully!")
    except BinanceAPIError as exc:
        _error(f"Binance API error: {exc}")
        logger.error("API error: %s", exc)
    except (ConnectionError, TimeoutError) as exc:
        _error(f"Network error: {exc}")
        logger.error("Network error: %s", exc)
    except Exception as exc:
        _error(f"Unexpected error: {exc}")
        logger.exception("Unexpected error while placing order")


def interactive_menu():
    click.echo(f"\n{Fore.CYAN}{'=' * 50}")
    click.echo("   PrimeTrade AI – Binance Futures Testnet Bot")
    click.echo(f"{'=' * 50}{Style.RESET_ALL}\n")

    while True:
        click.echo(f"{Fore.YELLOW}Choose an action:{Style.RESET_ALL}")
        click.echo("  1) Place an order")
        click.echo("  2) Check price")
        click.echo("  3) View account balances")
        click.echo("  4) Exit")

        choice = click.prompt("\nSelection", type=int, default=1)

        if choice == 1:
            _interactive_order()
        elif choice == 2:
            _interactive_price()
        elif choice == 3:
            _interactive_account()
        elif choice == 4:
            _info("Goodbye!")
            break
        else:
            _error("Invalid choice. Please enter 1-4.")
        click.echo()


def _interactive_order():
    click.echo(f"\n{Fore.CYAN}── Place Order ──{Style.RESET_ALL}")

    symbol = click.prompt("  Symbol", default="BTCUSDT")
    side = click.prompt("  Side (BUY/SELL)", type=click.Choice(["BUY", "SELL"], case_sensitive=False))
    order_type = click.prompt(
        "  Order type",
        type=click.Choice(["MARKET", "LIMIT", "STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"], case_sensitive=False),
    )
    quantity = click.prompt("  Quantity", type=float)

    price = None
    if order_type.upper() in {"LIMIT", "STOP", "TAKE_PROFIT"}:
        price = click.prompt("  Price", type=float)

    stop_price = None
    if order_type.upper() in {"STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"}:
        stop_price = click.prompt("  Stop price", type=float)

    if click.confirm("\n  Confirm order?", default=True):
        _execute_order(symbol, side, order_type, quantity, price, stop_price)
    else:
        _info("Order cancelled.")


def _interactive_price():
    symbol = click.prompt("  Symbol", default="BTCUSDT")
    try:
        client = BinanceClient()
        s = validate_symbol(symbol)
        data = client.ticker_price(s)
        _success(f"{data['symbol']} = {data['price']}")
    except Exception as exc:
        _error(str(exc))


def _interactive_account():
    try:
        client = BinanceClient()
        info = client.account_info()
        click.echo(f"\n{Fore.CYAN}  Account Balances (non-zero):{Style.RESET_ALL}")
        for asset in info.get("assets", []):
            balance = float(asset.get("walletBalance", 0))
            if balance != 0:
                click.echo(f"    {asset['asset']:>8s}  {balance:>14.4f}")
    except Exception as exc:
        _error(str(exc))



if __name__ == "__main__":
    cli()
