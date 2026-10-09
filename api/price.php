<?php

declare(strict_types=1);

/**
 * GET api/price.php -> {"updatedAt": "2026-10-09T10:30:00+03:30", "prices": {"pe100": 1850000, "pe80": 1700000}}
 * Prices are rials per kilogram; null means the admin has not set that material yet.
 */

require __DIR__ . '/../server/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
    http_response_code(405);
    header('Allow: GET, HEAD');
    echo '{"error":"method not allowed"}';
    exit;
}

try {
    $body = json_encode(Kabirloole\price_store()->read(), JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES);
    header('Cache-Control: public, max-age=60');
    echo $body;
} catch (Throwable $error) {
    error_log('[kabirloole] price API: ' . $error->getMessage());
    http_response_code(500);
    header('Cache-Control: no-store');
    echo '{"error":"unavailable"}';
}
