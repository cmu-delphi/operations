<?php
class Secrets {

  public static $db = array(
    'auto' => array('{SECRET_DB_USERNAME_AUTO}', '{SECRET_DB_PASSWORD_AUTO}'),
    'epi' => array('{SECRET_DB_USERNAME_EPI}', '{SECRET_DB_PASSWORD_EPI}')
  );

  public static $epicast = array(
    'captcha_key' => '{SECRET_EPICAST_CAPTCHA_KEY}'
  );

  public static $api = array(
    'twitter' => '{SECRET_API_AUTH_TWITTER}',
    'ght' => '{SECRET_API_AUTH_GHT}',
    'fluview' => '{SECRET_API_AUTH_FLUVIEW}',
    'cdc' => '{SECRET_API_AUTH_CDC}',
    'quidel' => '{SECRET_API_AUTH_QUIDEL}',
    'norostat' => '{SECRET_API_AUTH_NOROSTAT}',
    'sensors' => '{SECRET_API_AUTH_SENSORS}'
  );

  public static $flucontest = array(
    'hmac' => '{SECRET_FLUCONTEST_HMAC}'
  );

  public static $wiki = array(
    'hmac' => '{SECRET_WIKI_HMAC}'
  );

  public static $cdcp = array(
    'hmac' => '{SECRET_CDCP_HMAC}'
  );

}
?>
