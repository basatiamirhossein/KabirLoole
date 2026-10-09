<?php

declare(strict_types=1);

namespace Kabirloole;

use DateTimeImmutable;
use DateTimeZone;

ini_set('display_errors', '0');
ini_set('log_errors', '1');

foreach (['Material', 'LoginResult', 'PriceStore', 'LoginThrottle', 'AdminAuth'] as $class) {
    require_once __DIR__ . "/src/{$class}.php";
}

/** @return array{timezone: string, storage_dir: string, session_idle_seconds: int, login_max_attempts: int, login_lock_seconds: int, max_price_per_kg: int, history_size: int} */
function config(): array
{
    static $config = null;

    return $config ??= require __DIR__ . '/config.php';
}

date_default_timezone_set(config()['timezone']);

function now(): DateTimeImmutable
{
    return new DateTimeImmutable('now', new DateTimeZone(config()['timezone']));
}

function price_store(): PriceStore
{
    $c = config();

    return new PriceStore(
        $c['storage_dir'] . '/prices.json',
        $c['storage_dir'] . '/prices-history.jsonl',
        $c['max_price_per_kg'],
        $c['history_size'],
    );
}

function admin_auth(): AdminAuth
{
    $c = config();
    $throttle = new LoginThrottle($c['storage_dir'] . '/login-throttle.json', $c['login_max_attempts'], $c['login_lock_seconds']);

    return new AdminAuth($c['storage_dir'] . '/admin-password.php', $throttle, $c['session_idle_seconds']);
}
