include saas
saas::instance{ "{{ app_name }}":
  domain => "{{ app_domain }}",
  user   => {
    'username'   => '{{ app_user.username }}',
    'email'      => '{{ app_user.email }}',
    'password'   => '{{ app_user.password }}',
    'first_name' => "{{ app_user.first_name }}",
    'last_name'  => "{{ app_user.last_name }}",
  },
  ensure => {% if enabled %}'present'{% else %}'absent'{% endif %},
}
