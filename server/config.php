<?php

declare(strict_types=1);

/**
 * Server settings for the daily price API and the admin panel.
 * Prices are stored in Iranian rials per kilogram of pipe.
 */
return [
    'timezone' => 'Asia/Tehran',
    'storage_dir' => __DIR__ . '/storage',
    'session_idle_seconds' => 30 * 60,
    'login_max_attempts' => 5,
    'login_lock_seconds' => 15 * 60,
    'max_price_per_kg' => 100_000_000_000,
    'history_size' => 10,
];
