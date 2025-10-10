<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.22 -->
# __ae__ namespace-root project

ae namespace-root: bundling and maintaining templates and documentation of the portions of this namespace.


## ae namespace root package use-cases

this package is the root project of the ae namespace and their portions (the modules
and sub-packages of the namespace ae). it provides helpers and templates in order to
bundle and ease the maintenance, for example to:

* update and deploy common outsourced files, optionally generated from templates.
* merge docstrings of all portions into a single combined and cross-linked documentation.
* compile and publish documentation via Sphinx onto [ReadTheDocs](https://ae.readthedocs.io "ae on RTD").
* bulk refactor multiple portions of this namespace simultaneously using the
  [git repository manager tool (__pjm__)](https://gitlab.com/aedev-group/aedev_project_manager).

to enable the update and deployment of outsourced files generated from the templates provided by
this root package, add this root package to the development requirements file (dev_requirements.txt)
of each portion project of this namespace. in this entry you can optionally specify the version of
this project.

and because this namespace-root package is only needed for development tasks, it will never need to
be added to the installation requirements file (requirements.txt) of a project.

please check the [project manager manual](
https://aedev.readthedocs.io/en/latest/man/project_manager.html "project_manager manual")
for more detailed information on the provided actions of the __pjm__ tool.


## installation

no installation is needed to use this project for your portion projects, because the __pjm__ tool is
automatically fetching this and the other template projects from https://gitlab.com/ae-group (and
in the specified version).

an installation is only needed if you want to adapt this namespace-root project for your needs or if you want
to contribute to this root package. in this case please follow the instructions given in the
:ref:`contributing` document.


## namespace portions

the following 45 portions are currently included in this namespace:

* [ae_base](https://pypi.org/project/ae_base "ae namespace portion ae_base")
* [ae_deep](https://pypi.org/project/ae_deep "ae namespace portion ae_deep")
* [ae_django_utils](https://pypi.org/project/ae_django_utils "ae namespace portion ae_django_utils")
* [ae_notify](https://pypi.org/project/ae_notify "ae namespace portion ae_notify")
* [ae_valid](https://pypi.org/project/ae_valid "ae namespace portion ae_valid")
* [ae_files](https://pypi.org/project/ae_files "ae namespace portion ae_files")
* [ae_paths](https://pypi.org/project/ae_paths "ae namespace portion ae_paths")
* [ae_cloud_storage](https://pypi.org/project/ae_cloud_storage "ae namespace portion ae_cloud_storage")
* [ae_oaio_model](https://pypi.org/project/ae_oaio_model "ae namespace portion ae_oaio_model")
* [ae_oaio_client](https://pypi.org/project/ae_oaio_client "ae namespace portion ae_oaio_client")
* [ae_core](https://pypi.org/project/ae_core "ae namespace portion ae_core")
* [ae_dynamicod](https://pypi.org/project/ae_dynamicod "ae namespace portion ae_dynamicod")
* [ae_i18n](https://pypi.org/project/ae_i18n "ae namespace portion ae_i18n")
* [ae_parse_date](https://pypi.org/project/ae_parse_date "ae namespace portion ae_parse_date")
* [ae_literal](https://pypi.org/project/ae_literal "ae namespace portion ae_literal")
* [ae_updater](https://pypi.org/project/ae_updater "ae namespace portion ae_updater")
* [ae_console](https://pypi.org/project/ae_console "ae namespace portion ae_console")
* [ae_shell](https://pypi.org/project/ae_shell "ae namespace portion ae_shell")
* [ae_templates](https://pypi.org/project/ae_templates "ae namespace portion ae_templates")
* [ae_dev_ops](https://pypi.org/project/ae_dev_ops "ae namespace portion ae_dev_ops")
* [ae_pythonanywhere](https://pypi.org/project/ae_pythonanywhere "ae namespace portion ae_pythonanywhere")
* [ae_lockname](https://pypi.org/project/ae_lockname "ae namespace portion ae_lockname")
* [ae_progress](https://pypi.org/project/ae_progress "ae namespace portion ae_progress")
* [ae_sys_core](https://pypi.org/project/ae_sys_core "ae namespace portion ae_sys_core")
* [ae_sys_data](https://pypi.org/project/ae_sys_data "ae namespace portion ae_sys_data")
* [ae_sys_core_sh](https://pypi.org/project/ae_sys_core_sh "ae namespace portion ae_sys_core_sh")
* [ae_sys_data_sh](https://pypi.org/project/ae_sys_data_sh "ae namespace portion ae_sys_data_sh")
* [ae_db_core](https://pypi.org/project/ae_db_core "ae namespace portion ae_db_core")
* [ae_db_ora](https://pypi.org/project/ae_db_ora "ae namespace portion ae_db_ora")
* [ae_db_pg](https://pypi.org/project/ae_db_pg "ae namespace portion ae_db_pg")
* [ae_transfer_service](https://pypi.org/project/ae_transfer_service "ae namespace portion ae_transfer_service")
* [ae_sideloading_server](https://pypi.org/project/ae_sideloading_server "ae namespace portion ae_sideloading_server")
* [ae_gui](https://pypi.org/project/ae_gui "ae namespace portion ae_gui")
* [ae_kivy_glsl](https://pypi.org/project/ae_kivy_glsl "ae namespace portion ae_kivy_glsl")
* [ae_kivy_dyn_chi](https://pypi.org/project/ae_kivy_dyn_chi "ae namespace portion ae_kivy_dyn_chi")
* [ae_kivy_relief_canvas](https://pypi.org/project/ae_kivy_relief_canvas "ae namespace portion ae_kivy_relief_canvas")
* [ae_kivy](https://pypi.org/project/ae_kivy "ae namespace portion ae_kivy")
* [ae_kivy_auto_width](https://pypi.org/project/ae_kivy_auto_width "ae namespace portion ae_kivy_auto_width")
* [ae_kivy_file_chooser](https://pypi.org/project/ae_kivy_file_chooser "ae namespace portion ae_kivy_file_chooser")
* [ae_kivy_iterable_displayer](https://pypi.org/project/ae_kivy_iterable_displayer "ae namespace portion ae_kivy_iterable_displayer")
* [ae_kivy_qr_displayer](https://pypi.org/project/ae_kivy_qr_displayer "ae namespace portion ae_kivy_qr_displayer")
* [ae_kivy_sideloading](https://pypi.org/project/ae_kivy_sideloading "ae namespace portion ae_kivy_sideloading")
* [ae_kivy_user_prefs](https://pypi.org/project/ae_kivy_user_prefs "ae namespace portion ae_kivy_user_prefs")
* [ae_lisz_app_data](https://pypi.org/project/ae_lisz_app_data "ae namespace portion ae_lisz_app_data")
* [ae_enaml_app](https://pypi.org/project/ae_enaml_app "ae namespace portion ae_enaml_app")
