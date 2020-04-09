<?php

/*
This file is a drop-in replacement for the actual `secrets.php` used by various
Delphi frontends.

The "secret" values in this file aren't actually secret or sensitive as they
are used exclusively for local development.

This file needs to be kept in sync with `src/secrets.php`.
*/

class Secrets {

  public static $db = array(
    'auto' => array('user', 'pass'),
    'epi' => array('user', 'pass')
  );

  public static $epicast = array(
    'captcha_key' => 'secret'
  );

  public static $api = array(
    'twitter' => 'secret',
    'ght' => 'secret',
    'fluview' => 'secret',
    'cdc' => 'secret',
    'quidel' => 'secret',
    'norostat' => 'secret',
    'afhsb' => 'secret',
    'sensors' => 'secret',
    'sensor_subsets' => array(
      'twtr_sensor' => 'secret',
      'gft_sensor' => 'secret',
      'ght_sensors' => 'secret',
      'cdc_sensor' => 'secret',
      'quid_sensor' => 'secret',
      'wiki_sensor' => 'secret',
    ),
  );

  public static $flucontest = array(
    'hmac' => 'secret'
  );

  public static $wiki = array(
    'hmac' => 'secret'
  );

  public static $cdcp = array(
    'hmac' => 'secret'
  );

}
?>
