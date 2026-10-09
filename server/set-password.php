<?php

declare(strict_types=1);

/**
 * Set or change the admin panel password. Run from a terminal, on the server or on your own PC
 * before uploading:   php server/set-password.php
 * The hash is written to server/storage/admin-password.php, which outputs nothing if requested over HTTP.
 */

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

require __DIR__ . '/bootstrap.php';

const MIN_LENGTH = 10;

function ask(string $prompt): string
{
    fwrite(STDOUT, $prompt);
    $hide = DIRECTORY_SEPARATOR === '/' && stream_isatty(STDIN);
    if ($hide) {
        shell_exec('stty -echo');
    }
    $line = fgets(STDIN);
    if ($hide) {
        shell_exec('stty echo');
        fwrite(STDOUT, PHP_EOL);
    }

    return rtrim((string) $line, "\r\n");
}

$password = ask('New admin password: ');
if (preg_match_all('/./u', $password) < MIN_LENGTH) {
    fwrite(STDERR, 'Use at least ' . MIN_LENGTH . " characters.\n");
    exit(1);
}
if (ask('Repeat it: ') !== $password) {
    fwrite(STDERR, "The passwords do not match.\n");
    exit(1);
}

$dir = Kabirloole\config()['storage_dir'];
if (!is_dir($dir) && !mkdir($dir, 0750, true) && !is_dir($dir)) {
    fwrite(STDERR, "Cannot create {$dir}\n");
    exit(1);
}
$file = $dir . '/admin-password.php';
$code = "<?php\n\nreturn " . var_export(password_hash($password, PASSWORD_DEFAULT), true) . ";\n";
if (file_put_contents($file, $code, LOCK_EX) === false) {
    fwrite(STDERR, "Cannot write {$file}\n");
    exit(1);
}
chmod($file, 0640);
fwrite(STDOUT, "Saved. Sign in at /admin/\n");
