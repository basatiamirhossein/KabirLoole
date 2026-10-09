<?php

declare(strict_types=1);

namespace Kabirloole;

/** Locks an IP address out after too many failed logins. IPs are stored only as hashes. */
final class LoginThrottle
{
    public function __construct(
        private readonly string $file,
        private readonly int $maxAttempts,
        private readonly int $lockSeconds,
    ) {
    }

    public function isLocked(string $ip, int $now): bool
    {
        $entry = $this->load($now)[$this->key($ip)] ?? null;

        return $entry !== null && $entry['count'] >= $this->maxAttempts;
    }

    public function recordFailure(string $ip, int $now): void
    {
        $this->update($now, function (array $entries) use ($ip, $now): array {
            $key = $this->key($ip);
            $entry = $entries[$key] ?? ['count' => 0, 'first' => $now];
            $entries[$key] = ['count' => $entry['count'] + 1, 'first' => $entry['first']];

            return $entries;
        });
    }

    public function clear(string $ip, int $now): void
    {
        $this->update($now, function (array $entries) use ($ip): array {
            unset($entries[$this->key($ip)]);

            return $entries;
        });
    }

    private function key(string $ip): string
    {
        return hash('sha256', $ip);
    }

    /** @return array<string, array{count: int, first: int}> entries still inside the lock window */
    private function load(int $now): array
    {
        $raw = is_file($this->file) ? json_decode((string) file_get_contents($this->file), true) : [];
        $entries = [];
        foreach (is_array($raw) ? $raw : [] as $key => $entry) {
            if (is_string($key) && is_int($entry['count'] ?? null) && is_int($entry['first'] ?? null)
                && $now - $entry['first'] < $this->lockSeconds) {
                $entries[$key] = ['count' => $entry['count'], 'first' => $entry['first']];
            }
        }

        return $entries;
    }

    /** @param callable(array<string, array{count: int, first: int}>): array<string, array{count: int, first: int}> $change */
    private function update(int $now, callable $change): void
    {
        $handle = fopen($this->file, 'c+');
        if ($handle === false) {
            error_log('[kabirloole] cannot open login throttle file');

            return;
        }
        try {
            flock($handle, LOCK_EX);
            $entries = $change($this->load($now));
            ftruncate($handle, 0);
            rewind($handle);
            fwrite($handle, json_encode($entries, JSON_THROW_ON_ERROR));
            fflush($handle);
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }
    }
}
