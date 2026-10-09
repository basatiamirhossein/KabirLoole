<?php

declare(strict_types=1);

namespace Kabirloole;

/** Raw material of the pipe. The values match the site's calculator (pe100, pe80). */
enum Material: string
{
    case PE100 = 'pe100';
    case PE80 = 'pe80';

    public function label(): string
    {
        return strtoupper($this->value);
    }
}
