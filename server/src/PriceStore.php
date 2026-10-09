<?php

declare(strict_types=1);

namespace Kabirloole;

use DateTimeImmutable;
use DateTimeInterface;
use InvalidArgumentException;
use JsonException;
use RuntimeException;

/**
 * Daily price per kilogram for each raw material, kept in a JSON file with a short change history.
 *
 * @phpstan-type PriceList array{updatedAt: ?string, prices: array<string, ?int>}
 */
final class PriceStore
{
    public function __construct(
        private readonly string $file,
        private readonly string $historyFile,
        private readonly int $maxPrice,
        private readonly int $historySize,
    ) {
    }

    /** @return PriceList */
    public function read(): array
    {
        $empty = ['updatedAt' => null, 'prices' => array_fill_keys(array_column(Material::cases(), 'value'), null)];
        if (!is_file($this->file)) {
            return $empty;
        }
        $data = $this->decode((string) file_get_contents($this->file));
        $prices = $empty['prices'];
        foreach (Material::cases() as $material) {
            $value = $data['prices'][$material->value] ?? null;
            $prices[$material->value] = is_int($value) && $value > 0 ? $value : null;
        }
        $updatedAt = $data['updatedAt'] ?? null;

        return ['updatedAt' => is_string($updatedAt) ? $updatedAt : null, 'prices' => $prices];
    }

    /**
     * @param array<string, int> $prices keyed by Material value
     */
    public function save(array $prices, DateTimeImmutable $now): void
    {
        $clean = [];
        foreach (Material::cases() as $material) {
            $value = $prices[$material->value] ?? null;
            if (!is_int($value) || $value <= 0 || $value > $this->maxPrice) {
                throw new InvalidArgumentException("Invalid price for {$material->label()}");
            }
            $clean[$material->value] = $value;
        }
        $record = ['updatedAt' => $now->format(DateTimeInterface::ATOM), 'prices' => $clean];
        $this->writeAtomic($this->file, $this->encode($record));
        $this->appendHistory($record);
    }

    /** @return list<PriceList> newest first */
    public function history(): array
    {
        if (!is_file($this->historyFile)) {
            return [];
        }
        $lines = file($this->historyFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [];
        $entries = [];
        foreach (array_reverse($lines) as $line) {
            $entry = $this->decode($line);
            if (is_string($entry['updatedAt'] ?? null) && is_array($entry['prices'] ?? null)) {
                $entries[] = $entry;
            }
        }

        return $entries;
    }

    /** @param PriceList $record */
    private function appendHistory(array $record): void
    {
        $lines = array_map(fn (array $entry): string => $this->encode($entry), array_reverse($this->history()));
        $lines[] = $this->encode($record);
        $this->writeAtomic($this->historyFile, implode("\n", array_slice($lines, -$this->historySize)) . "\n");
    }

    /** @return array<string, mixed> */
    private function decode(string $json): array
    {
        try {
            $data = json_decode($json, true, 8, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            return [];
        }

        return is_array($data) ? $data : [];
    }

    /** @param array<string, mixed> $data */
    private function encode(array $data): string
    {
        return json_encode($data, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }

    private function writeAtomic(string $file, string $contents): void
    {
        $dir = dirname($file);
        if (!is_dir($dir) && !mkdir($dir, 0750, true) && !is_dir($dir)) {
            throw new RuntimeException("Cannot create {$dir}");
        }
        $tmp = tempnam($dir, 'tmp-');
        if ($tmp === false || file_put_contents($tmp, $contents, LOCK_EX) === false || !rename($tmp, $file)) {
            if (is_string($tmp) && is_file($tmp)) {
                unlink($tmp);
            }
            throw new RuntimeException("Cannot write {$file}");
        }
        chmod($file, 0640);
    }
}
