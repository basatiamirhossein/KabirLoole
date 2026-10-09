<?php

declare(strict_types=1);

namespace Kabirloole;

enum LoginResult
{
    case Ok;
    case Invalid;
    case Locked;
    case NotConfigured;
}
