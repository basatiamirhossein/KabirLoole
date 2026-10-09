<?php

declare(strict_types=1);

/** Admin panel: sign in and set today's price per kilogram for each raw material. */

use Kabirloole\AdminAuth;
use Kabirloole\LoginResult;
use Kabirloole\Material;
use Kabirloole\PriceStore;

use function Kabirloole\admin_auth;
use function Kabirloole\now;
use function Kabirloole\price_store;

require __DIR__ . '/../server/bootstrap.php';

header("Content-Security-Policy: default-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'");
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

const ASSET_VERSION = '2.0.0';
const LOCAL_DIGITS = [
    '۰' => '0', '۱' => '1', '۲' => '2', '۳' => '3', '۴' => '4', '۵' => '5', '۶' => '6', '۷' => '7', '۸' => '8', '۹' => '9',
    '٠' => '0', '١' => '1', '٢' => '2', '٣' => '3', '٤' => '4', '٥' => '5', '٦' => '6', '٧' => '7', '٨' => '8', '٩' => '9',
];

function h(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function fa_digits(string $text): string
{
    return strtr($text, array_flip(array_slice(LOCAL_DIGITS, 0, 10)) + [',' => '٬']);
}

function fa_price(?int $rials): string
{
    return $rials === null ? '–' : fa_digits(number_format($rials));
}

function fa_date(?string $iso): string
{
    if ($iso === null) {
        return '–';
    }
    try {
        $date = new DateTimeImmutable($iso);
    } catch (Exception) {
        return '–';
    }
    if (class_exists(IntlDateFormatter::class)) {
        $formatter = new IntlDateFormatter('fa_IR@calendar=persian', IntlDateFormatter::NONE, IntlDateFormatter::NONE, $date->getTimezone(), IntlDateFormatter::TRADITIONAL, 'd MMMM y، HH:mm');
        $text = $formatter->format($date);
        if (is_string($text)) {
            return $text;
        }
    }

    return fa_digits($date->format('Y-m-d H:i'));
}

/** Accepts Persian/Arabic digits and thousands separators; returns null for anything else. */
function parse_price(mixed $raw): ?int
{
    if (!is_string($raw)) {
        return null;
    }
    $digits = preg_replace('/[\s,٬\'_]/u', '', strtr($raw, LOCAL_DIGITS)) ?? '';

    return preg_match('/^[0-9]{1,12}$/', $digits) === 1 ? (int) $digits : null;
}

function flash(string $type, string $message): void
{
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

/** @return array{type: string, message: string}|null */
function take_flash(): ?array
{
    $flash = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);

    return is_array($flash) ? $flash : null;
}

function redirect_back(): never
{
    header('Location: ./', true, 303);
    exit;
}

function handle_login(AdminAuth $auth, string $ip, int $time): void
{
    $result = $auth->attempt((string) ($_POST['password'] ?? ''), $ip, $time);
    match ($result) {
        LoginResult::Ok => null,
        LoginResult::Invalid => flash('error', 'رمز عبور درست نیست.'),
        LoginResult::Locked => flash('error', 'به دلیل تلاش‌های ناموفق، ورود تا ۱۵ دقیقه بسته است.'),
        LoginResult::NotConfigured => flash('error', 'هنوز رمز پنل تعیین نشده است.'),
    };
}

function handle_save(PriceStore $store): void
{
    $prices = [];
    foreach (Material::cases() as $material) {
        $value = parse_price($_POST["price_{$material->value}"] ?? null);
        if ($value === null || $value <= 0) {
            flash('error', "قیمت هر کیلو {$material->label()} را به ریال و فقط با عدد وارد کنید.");

            return;
        }
        $prices[$material->value] = $value;
    }
    try {
        $store->save($prices, now());
        flash('ok', 'قیمت‌ها ذخیره شد و از همین حالا در ماشین‌حساب سایت استفاده می‌شود.');
    } catch (Throwable $error) {
        error_log('[kabirloole] saving prices failed: ' . $error->getMessage());
        flash('error', 'ذخیره نشد. دسترسی نوشتن پوشه‌ی server/storage را بررسی کنید.');
    }
}

$auth = admin_auth();
$store = price_store();
$auth->startSession();
$time = now()->getTimestamp();
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST') {
    $action = $_POST['action'] ?? '';
    if (!$auth->checkCsrf($_POST['csrf'] ?? null)) {
        flash('error', 'نشست منقضی شده است؛ دوباره تلاش کنید.');
    } elseif ($action === 'login') {
        handle_login($auth, $ip, $time);
    } elseif ($action === 'logout') {
        $auth->logout();
    } elseif ($action === 'save' && $auth->isLoggedIn($time)) {
        handle_save($store);
    }
    redirect_back();
}

$loggedIn = $auth->isLoggedIn($time);
$flash = take_flash();
$csrf = h($auth->csrfToken());
$current = $store->read();
?>
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>پنل قیمت روزانه | کبیر لوله</title>
<link rel="icon" type="image/png" sizes="32x32" href="../assets/img/logo-32.png">
<link rel="stylesheet" href="../assets/css/main.css?v=<?= ASSET_VERSION ?>">
<link rel="stylesheet" href="admin.css?v=<?= ASSET_VERSION ?>">
</head>
<body class="page-admin">
<div class="paper" aria-hidden="true"></div>
<main class="admin">
  <header class="admin__head">
    <img src="../assets/img/logo-192.png" width="56" height="56" alt="">
    <div><h1>پنل قیمت روزانه</h1><p>کبیر لوله</p></div>
  </header>

  <?php if ($flash !== null): ?>
    <p class="admin__flash admin__flash--<?= $flash['type'] === 'ok' ? 'ok' : 'error' ?>" role="status"><?= h((string) $flash['message']) ?></p>
  <?php endif; ?>

  <?php if (!$auth->isConfigured()): ?>
    <section class="admin__card neu">
      <h2>رمز پنل تعیین نشده است</h2>
      <p>در ترمینال سرور یا روی کامپیوتر خودتان پیش از آپلود این دستور را اجرا کنید:</p>
      <pre dir="ltr">php server/set-password.php</pre>
    </section>
  <?php elseif (!$loggedIn): ?>
    <form class="admin__card neu" method="post" action="./">
      <h2>ورود</h2>
      <input type="hidden" name="csrf" value="<?= $csrf ?>">
      <input type="hidden" name="action" value="login">
      <label class="field"><span class="field__label">رمز عبور</span>
        <input class="input neu-inset" type="password" name="password" autocomplete="current-password" required autofocus></label>
      <button class="btn btn--primary btn--block" type="submit">ورود به پنل</button>
    </form>
  <?php else: ?>
    <form class="admin__card neu" method="post" action="./">
      <h2>قیمت امروز هر کیلو لوله</h2>
      <p class="admin__muted">آخرین به‌روزرسانی: <?= h(fa_date($current['updatedAt'])) ?></p>
      <input type="hidden" name="csrf" value="<?= $csrf ?>">
      <input type="hidden" name="action" value="save">
      <?php foreach (Material::cases() as $material): ?>
        <label class="field"><span class="field__label">مواد اولیه <?= $material->label() ?>: قیمت هر کیلو (ریال)</span>
          <input class="input neu-inset" name="price_<?= $material->value ?>" inputmode="numeric" autocomplete="off" dir="ltr" required
            value="<?= h($current['prices'][$material->value] === null ? '' : number_format($current['prices'][$material->value])) ?>"></label>
      <?php endforeach; ?>
      <button class="btn btn--primary btn--block" type="submit">ذخیره قیمت‌ها</button>
    </form>

    <?php $history = $store->history(); ?>
    <?php if ($history !== []): ?>
      <section class="admin__card neu">
        <h2>تغییرات اخیر</h2>
        <table class="admin__table">
          <thead><tr><th scope="col">تاریخ</th><?php foreach (Material::cases() as $material): ?><th scope="col"><?= $material->label() ?></th><?php endforeach; ?></tr></thead>
          <tbody>
          <?php foreach ($history as $entry): ?>
            <tr><td><?= h(fa_date($entry['updatedAt'])) ?></td><?php foreach (Material::cases() as $material): ?><td><?= h(fa_price(is_int($entry['prices'][$material->value] ?? null) ? $entry['prices'][$material->value] : null)) ?></td><?php endforeach; ?></tr>
          <?php endforeach; ?>
          </tbody>
        </table>
      </section>
    <?php endif; ?>

    <div class="admin__foot">
      <a class="btn btn--neu" href="../fa/products.html#calculator">مشاهده ماشین‌حساب در سایت</a>
      <form method="post" action="./">
        <input type="hidden" name="csrf" value="<?= $csrf ?>">
        <input type="hidden" name="action" value="logout">
        <button class="btn btn--glass" type="submit">خروج</button>
      </form>
    </div>
  <?php endif; ?>
</main>
</body>
</html>
