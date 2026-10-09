<?php

declare(strict_types=1);

namespace Kabirloole;

/**
 * Single-admin login: a bcrypt/argon hash in storage/admin-password.php (written by
 * server/set-password.php), a hardened PHP session with an idle timeout, and CSRF tokens.
 */
final class AdminAuth
{
    private const SESSION_NAME = 'kl_admin';

    public function __construct(
        private readonly string $hashFile,
        private readonly LoginThrottle $throttle,
        private readonly int $idleSeconds,
    ) {
    }

    public function startSession(): void
    {
        if (session_status() === PHP_SESSION_ACTIVE) {
            return;
        }
        $https = ($_SERVER['HTTPS'] ?? '') !== '' && ($_SERVER['HTTPS'] ?? '') !== 'off';
        session_name(self::SESSION_NAME);
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'secure' => $https,
            'httponly' => true,
            'samesite' => 'Strict',
        ]);
        ini_set('session.use_strict_mode', '1');
        ini_set('session.use_only_cookies', '1');
        session_start();
    }

    public function isConfigured(): bool
    {
        return $this->passwordHash() !== null;
    }

    public function isLoggedIn(int $now): bool
    {
        $last = $_SESSION['admin_seen'] ?? null;
        if (!is_int($last) || $now - $last > $this->idleSeconds) {
            unset($_SESSION['admin_seen']);

            return false;
        }
        $_SESSION['admin_seen'] = $now;

        return true;
    }

    public function attempt(string $password, string $ip, int $now): LoginResult
    {
        $hash = $this->passwordHash();
        if ($hash === null) {
            return LoginResult::NotConfigured;
        }
        if ($this->throttle->isLocked($ip, $now)) {
            return LoginResult::Locked;
        }
        if (!password_verify($password, $hash)) {
            $this->throttle->recordFailure($ip, $now);

            return LoginResult::Invalid;
        }
        $this->throttle->clear($ip, $now);
        session_regenerate_id(true);
        $_SESSION = ['admin_seen' => $now, 'csrf' => bin2hex(random_bytes(32))];

        return LoginResult::Ok;
    }

    public function logout(): void
    {
        $_SESSION = [];
        session_regenerate_id(true);
    }

    public function csrfToken(): string
    {
        if (!is_string($_SESSION['csrf'] ?? null)) {
            $_SESSION['csrf'] = bin2hex(random_bytes(32));
        }

        return $_SESSION['csrf'];
    }

    public function checkCsrf(mixed $token): bool
    {
        return is_string($token) && is_string($_SESSION['csrf'] ?? null) && hash_equals($_SESSION['csrf'], $token);
    }

    private function passwordHash(): ?string
    {
        if (!is_file($this->hashFile)) {
            return null;
        }
        $hash = require $this->hashFile;

        return is_string($hash) && $hash !== '' ? $hash : null;
    }
}
