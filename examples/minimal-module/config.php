<?php

use example\minimal\Events;
use example\minimal\Module;
use humhub\modules\user\models\User;

return [
    'id' => 'minimal',
    'class' => Module::class,
    'namespace' => 'example\minimal',
    'events' => [
        [
            'class' => User::class,
            'event' => User::EVENT_AFTER_DELETE,
            'callback' => [Events::class, 'onUserAfterDelete'],
        ],
    ],
];
