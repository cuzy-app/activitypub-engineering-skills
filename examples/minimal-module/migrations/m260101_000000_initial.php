<?php

use humhub\components\Migration;

class m260101_000000_initial extends Migration
{
    public function up()
    {
        $this->createTable('minimal_item', [
            'id' => $this->primaryKey(),
            'title' => $this->string(255)->notNull(),
            'created_at' => $this->dateTime(),
        ]);
    }

    public function down()
    {
        $this->dropTable('minimal_item');
    }
}
