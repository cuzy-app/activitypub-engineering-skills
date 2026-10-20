<?php

namespace example\minimal;

use humhub\modules\user\models\User;
use yii\base\Event;

class Events
{
    public static function onUserAfterDelete(Event $event): void
    {
        if (!$event->sender instanceof User) {
            return;
        }

        // Remove or detach module data that belongs to the deleted user here.
    }
}
