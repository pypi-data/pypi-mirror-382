==================================================================
ansible-core 2.19 "What Is and What Should Never Be" Release Notes
==================================================================

.. contents:: Topics

v2.19.3
=======

Release Summary
---------------

| Release Date: 2025-10-06
| `Porting Guide <https://docs.ansible.com/ansible-core/2.19/porting_guides/porting_guide_core_2.19.html>`__

Minor Changes
-------------

- fetch_file - add ca_path and cookies parameter arguments (https://github.com/ansible/ansible/issues/85172).

Bugfixes
--------

- Windows async - Handle running PowerShell modules with trailing data after the module result
- ansible-doc --list/--list_files/--metadata-dump - fixed relative imports in nested filter/test plugin files (https://github.com/ansible/ansible/issues/85753).
- display - Fixed reference to undefined `_DeferredWarningContext` when issuing early warnings during startup. (https://github.com/ansible/ansible/issues/85886)
- run_command - Fixed premature selector unregistration on empty read from stdout/stderr that caused truncated output or hangs in rare situations.
- script inventory plugin will now show correct 'incorrect' type when doing implicit conversions on groups.

v2.19.2
=======

Release Summary
---------------

| Release Date: 2025-09-08
| `Porting Guide <https://docs.ansible.com/ansible-core/2.19/porting_guides/porting_guide_core_2.19.html>`__

Minor Changes
-------------

- ansible-test - Implement new authentication methods for accessing the Ansible Core CI service.

Bugfixes
--------

- The ``ansible_failed_task`` variable is now correctly exposed in a rescue section, even when a failing handler is triggered by the ``flush_handlers`` task in the corresponding ``block`` (https://github.com/ansible/ansible/issues/85682)
- ``ternary`` filter - evaluate values lazily (https://github.com/ansible/ansible/issues/85743)

v2.19.1
=======

Release Summary
---------------

| Release Date: 2025-08-25
| `Porting Guide <https://docs.ansible.com/ansible-core/2.19/porting_guides/porting_guide_core_2.19.html>`__

Minor Changes
-------------

- AnsibleModule - Add temporary internal monkeypatch-able hook to alter module result serialization by splitting serialization from ``_return_formatted`` into ``_record_module_result``.
- ansible-test - Improve formatting of generated coverage config file.
- ansible-test - Use OS packages to satisfy controller requirements on FreeBSD 13.5 during managed instance bootstrapping.
- encrypt - check datatype of salt_size in password_hash filter.
- service_facts - handle keyerror exceptions with warning.
- service_facts - warn user about missing service details instead of ignoring.

Bugfixes
--------

- ansible-test - Always exclude the ``tests/output/`` directory from a collection's code coverage. (https://github.com/ansible/ansible/issues/84244)
- ansible-test - Limit package install retries during managed remote instance bootstrapping.
- ansible-test - Use a consistent coverage config for all collection testing.
- argspec validation - The ``str`` argspec type treats ``None`` values as empty string for better consistency with pre-2.19 templating conversions.
- conditionals - When displaying a broken conditional error or deprecation warning, the origin of the non-boolean result is included (if available), and the raw result is omitted.
- failed_when - When using ``failed_when`` to suppress an error, the ``exception`` key in the result is renamed to ``failed_when_suppressed_exception``. This prevents the error from being displayed by callbacks after being suppressed. (https://github.com/ansible/ansible/issues/85505)
- import_tasks - fix templating parent include arguments.
- plugins config, get_option_and_origin now correctly displays the value and origin of the option.
- template lookup - Skip finalization on the internal templating operation to allow markers to be returned and handled by, e.g. the ``default`` filter. Previously, finalization tripped markers, causing an exception to end processing of the current template pipeline. (https://github.com/ansible/ansible/issues/85674)
- templating - Avoid tripping markers within Jinja generated code. (https://github.com/ansible/ansible/issues/85674)
- templating - Ensure filter plugin result processing occurs under the correct call context. (https://github.com/ansible/ansible/issues/85585)
- templating - Fix slicing of tuples in templating (https://github.com/ansible/ansible/issues/85606).
- templating - Multi-node template results coerce embedded ``None`` nodes to empty string (instead of rendering literal ``None`` to the output).
- templating - Undefined marker values sourced from the Jinja ``getattr->getitem`` fallback are now accessed correctly, raising AnsibleUndefinedVariable for user plugins that do not understand markers. Previously, these values were erroneously returned to user plugin code that had not opted in to marker acceptance.
- tqm - use display.error_as_warning instead of display.warning_as_error.
- tqm - use display.error_as_warning instead of self.warning.

v2.19.0
=======

Release Summary
---------------

| Release Date: 2025-07-21
| `Porting Guide <https://docs.ansible.com/ansible-core/2.19/porting_guides/porting_guide_core_2.19.html>`__

Major Changes
-------------

- Jinja plugins - Jinja builtin filter and test plugins are now accessible via their fully-qualified names ``ansible.builtin.{name}``.
- Task Execution / Forks - Forks no longer inherit stdio from the parent ``ansible-playbook`` process. ``stdout``, ``stderr``, and ``stdin`` within a worker are detached from the terminal, and non-functional. All needs to access stdio from a fork for controller side plugins requires use of ``Display``.
- ansible-test - Packages beneath ``module_utils`` can now contain ``__init__.py`` files.
- variables - The type system underlying Ansible's variable storage has been significantly overhauled and formalized. Attempts to store unsupported Python object types in variables now more consistently yields early warnings or errors.
- variables - To support new Ansible features, many variable objects are now represented by subclasses of their respective native Python types. In most cases, they behave indistinguishably from their original types, but some Python libraries do not handle builtin object subclasses properly. Custom plugins that interact with such libraries may require changes to convert and pass the native types.

Minor Changes
-------------

- Added a -vvvvv log message indicating when a host fails to produce output within the timeout period.
- Added type annotations to the ``Role.__init__()`` method to enable type checking. (https://github.com/ansible/ansible/pull/85346)
- AnsibleModule.uri - Add option ``multipart_encoding`` for ``form-multipart`` files in body to change default base64 encoding for files
- INVENTORY_IGNORE_EXTS config, removed ``ini`` from the default list, inventory scripts using a corresponding .ini configuration are rare now and inventory.ini files are more common. Those that need to ignore the ini files for inventory scripts can still add it to configuration.
- Improved SUSE distribution detection in distribution.py by parsing VARIANT_ID from /etc/os-release for identifying SLES_SAP and SL-Micro. Falls back to /etc/products.d/baseproduct symlink for older systems.
- Jinja plugins - Plugins can declare support for undefined values.
- Jinja2 version 3.1.0 or later is now required on the controller.
- Move ``follow_redirects`` parameter to module_utils so external modules can reuse it.
- PlayIterator - do not return tasks from already executed roles so specific strategy plugins do not have to do the filtering of such tasks themselves
- Remove unnecessary shebang from the ``hostname`` module.
- SSH Escalation-related -vvv log messages now include the associated host information.
- Use ``importlib.metadata.version()`` to detect Jinja version as jinja2.__version__ is deprecated and will be removed in Jinja 3.3.
- Windows - Add support for Windows Server 2025 to Ansible and as an ``ansible-test`` remote target - https://github.com/ansible/ansible/issues/84229
- Windows - refactor the async implementation to better handle errors during bootstrapping and avoid WMI when possible.
- ``ansible-galaxy collection install`` — the collection dependency resolver now prints out conflicts it hits during dependency resolution when it's taking too long and it ends up backtracking a lot. It also displays suggestions on how to help it compute the result more quickly.
- ansiballz - Added an experimental AnsiballZ extension for remote debugging.
- ansiballz - Added support for AnsiballZ extensions.
- ansiballz - Moved AnsiballZ code coverage support into an extension.
- ansiballz - Refactored AnsiballZ and module respawn.
- ansible, ansible-console, ansible-pull - add --flush-cache option (https://github.com/ansible/ansible/issues/83749).
- ansible-config will now show internal, but not test configuration entries. This allows for debugging but still denoting the configurations as internal use only (_ prefix).
- ansible-doc - Return dynamic stub when reporting on Jinja filters and tests not explicitly documented in Ansible
- ansible-doc - Skip listing the internal ``ansible._protomatter`` plugins unless explicitly requested
- ansible-galaxy - Add support for Keycloak service accounts
- ansible-galaxy - support ``resolvelib >= 0.5.3, < 2.0.0`` (https://github.com/ansible/ansible/issues/84217).
- ansible-test - Add RHEL 10.0 as a remote platform for testing.
- ansible-test - Added a macOS 15.3 remote VM, replacing 14.3.
- ansible-test - Added experimental support for remote debugging.
- ansible-test - Added support for setting static environment variables in integration tests using ``env/set/`` entries in the ``aliases`` file. For example, ``env/set/MY_KEY/MY_VALUE`` or ``env/set/MY_PATH//an/abs/path``.
- ansible-test - Automatically retry HTTP GET/PUT/DELETE requests on exceptions.
- ansible-test - Default to Python 3.13 in the ``base`` and ``default`` containers.
- ansible-test - Disable the ``deprecated-`` prefixed ``pylint`` rules as their results vary by Python version.
- ansible-test - Disable the ``pep8`` sanity test rules ``E701`` and ``E704`` to improve compatibility with ``black``.
- ansible-test - Improve container runtime probe error handling. When unexpected probe output is encountered, an error with more useful debugging information is provided.
- ansible-test - Improved ``pylint`` checks for Ansible-specific deprecation functions.
- ansible-test - Replace container Alpine 3.20 with 3.21.
- ansible-test - Replace container Fedora 40 with 41.
- ansible-test - Replace remote Alpine 3.20 with 3.21.
- ansible-test - Replace remote Fedora 40 with 41.
- ansible-test - Replace remote FreeBSD 13.3 with 13.5.
- ansible-test - Replace remote FreeBSD 14.1 with 14.2.
- ansible-test - Replace remote RHEL 9.4 with 9.5.
- ansible-test - Show a more user-friendly error message when a ``runme.sh`` script is not executable.
- ansible-test - The ``shell`` command has been augmented to propagate remote debug configurations and other test-related settings when running on the controller. Use the ``--raw`` argument to bypass the additional environment configuration.
- ansible-test - The ``yamllint`` sanity test now enforces string values for the ``!vault`` tag.
- ansible-test - Update ``nios-test-container`` to version 7.0.0.
- ansible-test - Update ``pylint`` sanity test to use version 3.3.1.
- ansible-test - Update distro containers to remove unnecessary packages (apache2, subversion, ruby).
- ansible-test - Update sanity test requirements to latest available versions.
- ansible-test - Update the HTTP test container.
- ansible-test - Update the PyPI test container.
- ansible-test - Update the ``base`` and ``default`` containers.
- ansible-test - Update the utility container.
- ansible-test - Use Python's ``urllib`` instead of ``curl`` for HTTP requests.
- ansible-test - Use the ``-t`` option to set the stop timeout when stopping a container. This avoids use of the ``--time`` option which was deprecated in Docker v28.0.
- ansible-test - When detection of the current container network fails, a warning is now issued and execution continues. This simplifies usage in cases where the current container cannot be inspected, such as when running in GitHub Codespaces.
- ansible-test acme test container - bump `version to 2.3.0 <https://github.com/ansible/acme-test-container/releases/tag/2.3.0>`__ to include newer versions of Pebble, dependencies, and runtimes. This adds support for ACME profiles, ``dns-account-01`` support, and some smaller improvements (https://github.com/ansible/ansible/pull/84547).
- apt - consider lock timeout while invoking apt-get command (https://github.com/ansible/ansible/issues/78658).
- apt_key module - add notes to docs and errors to point at the CLI tool deprecation by Debian and alternatives
- apt_repository - remove Python 2 support
- apt_repository module - add notes to errors to point at the CLI tool deprecation by Debian and alternatives
- assemble action added check_mode support
- become plugins get new property 'pipelining' to show support or lack there of for the feature.
- callback plugins - add has_option() to CallbackBase to match other functions overloaded from AnsiblePlugin
- callback plugins - fix get_options() for CallbackBase
- collection metadata - The collection loader now parses scalar values from ``meta/runtime.yml`` as strings. This avoids issues caused by unquoted values such as versions or dates being parsed as types other than strings.
- comment filter - Improve the error message shown when an invalid ``style`` argument is provided.
- copy - fix sanity test failures (https://github.com/ansible/ansible/pull/83643).
- copy - parameter ``local_follow`` was incorrectly documented as having default value ``True`` (https://github.com/ansible/ansible/pull/83643).
- cron - Provide additional error information while writing cron file (https://github.com/ansible/ansible/issues/83223).
- csvfile - let the config system do the typecasting (https://github.com/ansible/ansible/pull/82263).
- csvfile lookup - remove Python 2 compat
- deprecation warnings - Deprecation warning APIs automatically capture the identity of the deprecating plugin. The ``collection_name`` argument is only required to correctly attribute deprecations that occur in module_utils or other non-plugin code.
- deprecation warnings - Improved deprecation messages to more clearly indicate the affected content, including plugin name when available.
- deprecations - Collection name strings not of the form ``ns.coll`` passed to deprecation API functions will result in an error.
- deprecations - Removed support for specifying deprecation dates as a ``datetime.date``, which was included in an earlier 2.19 pre-release.
- deprecations - Some argument names to ``deprecate_value`` for consistency with existing APIs. An earlier 2.19 pre-release included a ``removal_`` prefix on the ``date`` and ``version`` arguments.
- display - Add ``help_text`` and ``obj`` to ``Display.error_as_warning``.
- display - Deduplication of warning and error messages considers the full content of the message (including source and traceback contexts, if enabled). This may result in fewer messages being omitted.
- display - Replace Windows newlines (``\r\n``) in display output with Unix newlines (``\n``). This ensures proper display of strings sourced from Windows hosts in environments which treat ``\r`` as ``\n``, such as Azure Pipelines.
- display - The ``formatted`` arg to ``warning`` has no effect. Warning wrapping is left to the consumer (e.g. terminal, browser).
- display - The ``wrap_text`` and ``stderr`` arguments to ``error`` have no effect. Errors are always sent to stderr and wrapping is left to the consumer (e.g. terminal, browser).
- distribution - Added openSUSE MicroOS to Suse OS family (#84685).
- dnf5, apt - add ``auto_install_module_deps`` option (https://github.com/ansible/ansible/issues/84206)
- docs - add collection name in message from which the module is being deprecated (https://github.com/ansible/ansible/issues/84116).
- env lookup - The error message generated for a missing environment variable when ``default`` is an undefined value (e.g. ``undef('something')``) will contain the hint from that undefined value, except when the undefined value is the default of ``undef()`` with no arguments. Previously, any existing undefined hint would be ignored.
- facts - add "CloudStack KVM Hypervisor" for Linux VM in virtual facts (https://github.com/ansible/ansible/issues/85089).
- facts - add "Linode" for Linux VM in virtual facts
- file - enable file module to disable diff_mode (https://github.com/ansible/ansible/issues/80817).
- file - make code more readable and simple.
- filter - add support for URL-safe encoding and decoding in b64encode and b64decode (https://github.com/ansible/ansible/issues/84147).
- find - add a checksum_algorithm parameter to specify which type of checksum the module will return
- from_json filter - The filter accepts a ``profile`` argument, which defaults to ``tagless``.
- handlers - Templated handler names with syntax errors, or that resolve to ``omit`` are now skipped like handlers with undefined variables in their name.
- improved error message for yaml parsing errors in plugin documentation
- local connection plugin - A new ``become_strip_preamble`` config option (default True) was added; disable to preserve diagnostic ``become`` output in task results.
- local connection plugin - A new ``become_success_timeout`` operation-wide timeout config (default 10s) was added for ``become``.
- local connection plugin - When a ``become`` plugin's ``prompt`` value is a non-string after the ``check_password_prompt`` callback has completed, no prompt stripping will occur on stderr.
- lookup_template - add an option to trim blocks while templating (https://github.com/ansible/ansible/issues/75962).
- module - set ipv4 and ipv6 rules simultaneously in iptables module (https://github.com/ansible/ansible/issues/84404).
- module_utils - Add ``AnsibleModule.error_as_warning``.
- module_utils - Add ``NoReturn`` type annotations to functions which never return.
- module_utils - Add ``ansible.module_utils.common.warnings.error_as_warning``.
- module_utils - Add optional ``help_text`` argument to ``AnsibleModule.warn``.
- module_utils.basic.backup_local enforces check_mode now
- modules - PowerShell modules can now receive ``datetime.date``, ``datetime.time`` and ``datetime.datetime`` values as ISO 8601 strings.
- modules - PowerShell modules can now receive strings sourced from inline vault-encrypted strings.
- modules - The ``AnsibleModule.deprecate`` function no longer sends deprecation messages to the target host's logging system.
- modules - Unhandled exceptions during Python module execution are now returned as structured data from the target. This allows the new traceback handling to be applied to exceptions raised on targets.
- modules - use ``AnsibleModule.warn`` instead of passing ``warnings`` to ``exit_json`` or ``fail_json`` which is deprecated.
- pipelining logic has mostly moved to connection plugins so they can decide/override settings.
- plugin error handling - When raising exceptions in an exception handler, be sure to use ``raise ... from`` as appropriate. This supersedes the use of the ``AnsibleError`` arg ``orig_exc`` to represent the cause. Specifying ``orig_exc`` as the cause is still permitted. Failure to use ``raise ... from`` when ``orig_exc`` is set will result in a warning. Additionally, if the two cause exceptions do not match, a warning will be issued.
- removed hardcoding of su plugin as it now works with pipelining.
- runtime-metadata sanity test - improve validation of ``action_groups`` (https://github.com/ansible/ansible/pull/83965).
- service_facts module got freebsd support added.
- ssh agent - Added ``SSH_AGENT_EXECUTABLE`` config to allow override of ssh-agent.
- ssh connection plugin - Added ``verbosity`` config to decouple SSH debug output verbosity from Ansible verbosity. Previously, the Ansible verbosity value was always applied to the SSH client command-line, leading to excessively verbose output. Set the ``ANSIBLE_SSH_VERBOSITY`` envvar or ``ansible_ssh_verbosity`` Ansible variable to a positive integer to increase SSH client verbosity.
- ssh connection plugin - Support ``SSH_ASKPASS`` mechanism to provide passwords, making it the default, but still offering an explicit choice to use ``sshpass`` (https://github.com/ansible/ansible/pull/83936)
- ssh connection plugin now overrides pipelining when a tty is requested.
- ssh-agent - ``ansible``, ``ansible-playbook`` and ``ansible-console`` are capable of spawning or reusing an ssh-agent, allowing plugins to interact with the ssh-agent. Additionally a pure python ssh-agent client has been added, enabling easy interaction with the agent. The ssh connection plugin contains new functionality via ``ansible_ssh_private_key`` and ``ansible_ssh_private_key_passphrase``, for loading an SSH private key into the agent from a variable.
- task timeout - Specifying a timeout greater than 100,000,000 now results in an error.
- template action and lookup plugin - The value of the ``ansible_managed`` variable (if set) will not be masked by the ``template`` action and lookup. Previously, the value calculated by the ``DEFAULT_MANAGED_STR`` configuration option always masked the variable value during plugin execution, preventing runtime customization.
- templating - Access to an undefined variable from inside a lookup, filter, or test (which raises MarkerError) no longer ends processing of the current template. The triggering undefined value is returned as the result of the offending plugin invocation, and the template continues to execute.
- templating - Added ``_ANSIBLE_TEMPLAR_SANDBOX_MODE=allow_unsafe_attributes`` environment variable to disable Jinja template attribute sandbox. (https://github.com/ansible/ansible/issues/85202)
- templating - Embedding ``range()`` values in containers such as lists will result in an error on use. Previously the value would be converted to a string representing the range parameters, such as ``range(0, 3)``.
- templating - Handling of omitted values is now a first-class feature of the template engine, and is usable in all Ansible Jinja template contexts. Any template that resolves to ``omit`` is automatically removed from its parent container during templating.
- templating - Relaxed the Jinja sandbox to allow specific bitwise operations which have no filter equivalent. The allowed methods are ``__and__``, ``__lshift__``, ``__or__``, ``__rshift__``, ``__xor__``.
- templating - Switched from the Jinja immutable sandbox to the standard sandbox. This restores the ability to use mutation methods such as ``list.append`` and ``dict.update``.
- templating - Template evaluation is lazier than in previous versions. Template expressions which resolve only portions of a data structure no longer result in the entire structure being templated.
- templating - Templating errors now provide more information about both the location and context of the error, especially for deeply-nested and/or indirected templating scenarios.
- templating - Unified ``omit`` behavior now requires that plugins calling ``Templar.template()`` handle cases where the entire template result is omitted, by catching the ``AnsibleValueOmittedError`` that is raised. Previously, this condition caused a randomly-generated string marker to appear in the template result.
- templating - Variables of type ``set`` and ``tuple`` are now converted to ``list`` when exiting the final pass of templating.
- to_json / to_nice_json filters - The filters accept a ``profile`` argument, which defaults to ``tagless``.
- troubleshooting - Tracebacks can be collected and displayed for most errors, warnings, and deprecation warnings (including those generated by modules). Tracebacks are no longer enabled with ``-vvv``; the behavior is directly configurable via the ``DISPLAY_TRACEBACK`` config option. Module tracebacks passed to ``fail_json`` via the ``exception`` kwarg will not be included in the task result unless error tracebacks are configured.
- undef jinja function - The ``undef`` jinja function now raises an error if a non-string hint is given. Attempting to use an undefined hint also results in an error, ensuring incorrect use of the function can be distinguished from the function's normal behavior.
- validate-modules sanity test - make sure that ``module`` and ``plugin`` ``seealso`` entries use FQCNs (https://github.com/ansible/ansible/pull/84325).
- variables - Removed restriction on usage of most Python keywords as Ansible variable names.
- variables - Warnings about reserved variable names now show context where the variable was defined.
- vault - improved vault filter documentation by adding missing example content for dump_template_data.j2, refining examples for clarity, and ensuring variable consistency (https://github.com/ansible/ansible/issues/83583).
- warnings - All warnings (including deprecation warnings) issued during a task's execution are now accessible via the ``warnings`` and ``deprecations`` keys on the task result.
- when the ``dict`` lookup is given a non-dict argument, show the value of the argument and its type in the error message.
- windows - Added support for ``#AnsibleRequires -Wrapper`` to request a PowerShell module be run through the execution wrapper scripts without any module utils specified.
- windows - Added support for running signed modules and scripts with a Windows host protected by Windows App Control/WDAC. This is a tech preview and the interface may be subject to change.
- windows - Script modules will preserve UTF-8 encoding when executing the script.
- windows - add hard minimum limit for PowerShell to 5.1. Ansible dropped support for older versions of PowerShell in the 2.16 release but this requirement is now enforced at runtime.
- windows - refactor windows exec runner to improve efficiency and add better error reporting on failures.
- winrm - Remove need for pexpect on macOS hosts when using ``kinit`` to retrieve the Kerberos TGT. By default the code will now only use the builtin ``subprocess`` library which should handle issues with select and a high fd count and also simplify the code.

Breaking Changes / Porting Guide
--------------------------------

- Support for the ``toml`` library has been removed from TOML inventory parsing and dumping. Use ``tomli`` for parsing on Python 3.10. Python 3.11 and later have built-in support for parsing. Use ``tomli-w`` to support outputting inventory in TOML format.
- assert - The ``quiet`` argument must be a commonly-accepted boolean value. Previously, unrecognized values were silently treated as False.
- conditionals - Conditional expressions that result in non-boolean values are now an error by default. Such results often indicate unintentional use of templates where they are not supported, resulting in a conditional that is always true. When this option is enabled, conditional expressions which are a literal ``None`` or empty string will evaluate as true, for backwards compatibility. The error can be temporarily changed to a deprecation warning by enabling the ``ALLOW_BROKEN_CONDITIONALS`` config option.
- first_found lookup - When specifying ``files`` or ``paths`` as a templated list containing undefined values, the undefined list elements will be discarded with a warning. Previously, the entire list would be discarded without any warning.
- internals - The ``AnsibleLoader`` and ``AnsibleDumper`` classes for working with YAML are now factory functions and cannot be extended.
- internals - The ``ansible.utils.native_jinja`` Python module has been removed.
- lookup plugins - Lookup plugins called as `with_(lookup)` will no longer have the `_subdir` attribute set.
- lookup plugins - ``terms`` will always be passed to ``run`` as the first positional arg, where previously it was sometimes passed as a keyword arg when using ``with_`` syntax.
- loops - Omit placeholders no longer leak between loop item templating and task templating. Previously, ``omit`` placeholders could remain embedded in loop items after templating and be used as an ``omit`` for task templating. Now, values resolving to ``omit`` are dropped immediately when loop items are templated. To turn missing values into an ``omit`` for task templating, use ``| default(omit)``. This solution is backward-compatible with previous versions of ansible-core.
- modules - Ansible modules using ``sys.excepthook`` must use a standard ``try/except`` instead.
- plugins - Any plugin that sources or creates templates must properly tag them as trusted.
- plugins - Custom Jinja plugins that accept undefined top-level arguments must opt in to receiving them.
- plugins - Custom Jinja plugins that use ``environment.getitem`` to retrieve undefined values will now trigger a ``MarkerError`` exception. This exception must be handled to allow the plugin to return a ``Marker``, or the plugin must opt-in to accepting ``Marker`` values.
- public API - The ``ansible.vars.fact_cache.FactCache`` wrapper has been removed.
- serialization of ``omit`` sentinel - Serialization of variables containing ``omit`` sentinels (e.g., by the ``to_json`` and ``to_yaml`` filters or ``ansible-inventory``) will fail if the variable has not completed templating. Previously, serialization succeeded with placeholder strings emitted in the serialized output.
- set_fact - The string values "yes", "no", "true" and "false" were previously converted (ignoring case) to boolean values when not using Jinja2 native mode. Since Jinja2 native mode is always used, this conversion no longer occurs. When boolean values are required, native boolean syntax should be used where variables are defined, such as in YAML. When native boolean syntax is not an option, the ``bool`` filter can be used to parse string values into booleans.
- template lookup - The ``convert_data`` option is deprecated and no longer has any effect. Use the ``from_json`` filter on the lookup result instead.
- templating - Access to ``_`` prefixed attributes and methods, and methods with known side effects, is no longer permitted. In cases where a matching mapping key is present, the associated value will be returned instead of an error. This increases template environment isolation and ensures more consistent behavior between the ``.`` and ``[]`` operators.
- templating - Conditionals and lookups which use embedded inline templates in Jinja string constants now display a warning. These templates should be converted to their expression equivalent.
- templating - Many Jinja plugins (filters, lookups, tests) and methods previously silently ignored undefined inputs, which often masked subtle errors. Passing an undefined argument to a Jinja plugin or method that does not declare undefined support now results in an undefined value.
- templating - Templates are always rendered in Jinja2 native mode. As a result, non-string values are no longer automatically converted to strings.
- templating - Templates resulting in ``None`` are no longer automatically converted to an empty string.
- templating - Templates with embedded inline templates that were not contained within a Jinja string constant now result in an error, as support for multi-pass templating was removed for security reasons. In most cases, such templates can be easily rewritten to avoid the use of embedded inline templates.
- templating - The ``allow_unsafe_lookups`` option no longer has any effect. Lookup plugins are responsible for tagging strings containing templates to allow evaluation as a template.
- templating - The result of the ``range()`` global function cannot be returned from a template- it should always be passed to a filter (e.g., ``random``). Previously, range objects returned from an intermediate template were always converted to a list, which is inconsistent with inline consumption of range objects.
- templating - ``#jinja2:`` overrides in templates with invalid override names or types are now templating errors.

Deprecated Features
-------------------

- CLI - The ``--inventory-file`` option alias is deprecated. Use the ``-i`` or ``--inventory`` option instead.
- Jinja test plugins - Returning a non-boolean result from a Jinja test plugin is deprecated.
- Passing a ``warnings` or ``deprecations`` key to ``exit_json`` or ``fail_json`` is deprecated. Use ``AnsibleModule.warn`` or ``AnsibleModule.deprecate`` instead.
- Strategy Plugins - Use of strategy plugins not provided in ``ansible.builtin`` are deprecated and do not carry any backwards compatibility guarantees going forward. A future release will remove the ability to use external strategy plugins. No alternative for third party strategy plugins is currently planned.
- The ``ShellModule.checksum`` method is now deprecated and will be removed in ansible-core 2.23. Use ``ActionBase._execute_remote_stat()`` instead.
- The ``ansible.module_utils.common.collections.count()`` function is deprecated and will be removed in ansible-core 2.23. Use ``collections.Counter()`` from the Python standard library instead.
- YAML parsing - Usage of the YAML 1.1 ``!!omap`` and ``!!pairs`` tags is deprecated. Use standard mappings instead.
- YAML parsing - Usage of the undocumented ``!vault-encrypted`` YAML tag is deprecated. Use ``!vault`` instead.
- ``ansible.compat.importlib_resources`` is deprecated and will be removed in ansible-core 2.23. Use ``importlib.resources`` from the Python standard library instead.
- ``ansible.module_utils.compat.datetime`` - The datetime compatibility shims are now deprecated. They are scheduled to be removed in ``ansible-core`` v2.21. This includes ``UTC``, ``utcfromtimestamp()`` and ``utcnow`` importable from said module (https://github.com/ansible/ansible/pull/81874).
- bool filter - Support for coercing unrecognized input values (including None) has been deprecated. Consult the filter documentation for acceptable values, or consider use of the ``truthy`` and ``falsy`` tests.
- cache plugins - The `ansible.plugins.cache.base` Python module is deprecated. Use `ansible.plugins.cache` instead.
- callback plugins - The `v2_on_any` callback method is deprecated. Use specific callback methods instead.
- callback plugins - The v1 callback API (callback methods not prefixed with `v2_`) is deprecated. Use `v2_` prefixed methods instead.
- conditionals - Conditionals using Jinja templating delimiters (e.g., ``{{``, ``{%``) should be rewritten as expressions without delimiters, unless the entire conditional value is a single template that resolves to a trusted string expression. This is useful for dynamic indirection of conditional expressions, but is limited to trusted literal string expressions.
- config - The ``ACTION_WARNINGS`` config has no effect. It previously disabled command warnings, which have since been removed.
- config - The ``DEFAULT_ALLOW_UNSAFE_LOOKUPS`` configuration option is deprecated and no longer has any effect. Ansible templating no longer encounters situations where use of lookup plugins is considered "unsafe".
- config - The ``DEFAULT_JINJA2_NATIVE`` option has no effect. Jinja2 native mode is now the default and only option.
- config - The ``DEFAULT_NULL_REPRESENTATION`` option has no effect. Null values are no longer automatically converted to another value during templating of single variable references.
- config - The ``DEFAULT_UNDEFINED_VAR_BEHAVIOR`` configuration option is deprecated and no longer has any effect. Attempting to use an undefined variable where undefined values are unexpected is now always an error. This behavior was enabled by default in previous versions, and disabling it yielded inconsistent results.
- config - The ``STRING_TYPE_FILTERS`` configuration option is deprecated and no longer has any effect. Since the template engine now always preserves native types, there is no longer a risk of unintended conversion from strings to native types.
- config - Using the ``DEFAULT_JINJA2_EXTENSIONS`` configuration option to enable Jinja2 extensions is deprecated. Previously, custom Jinja extensions were disabled by default, as they can destabilize the Ansible templating environment. Templates should only make use of filter, test and lookup plugins.
- config - Using the ``DEFAULT_MANAGED_STR`` configuration option to customize the value of the ``ansible_managed`` variable is deprecated. The ``ansible_managed`` variable can now be set the same as any other variable.
- display - The ``Display.get_deprecation_message`` method has been deprecated. Call ``Display.deprecated`` to display a deprecation message, or call it with ``removed=True`` to raise an ``AnsibleError``.
- file loading - Loading text files with ``DataLoader`` containing data that cannot be decoded under the expected encoding is deprecated. In most cases the encoding must be UTF-8, although some plugins allow choosing a different encoding. Previously, invalid data was silently wrapped in Unicode surrogate escape sequences, often resulting in later errors or other data corruption.
- first_found lookup - Splitting of file paths on ``,;:`` is deprecated. Pass a list of paths instead. The ``split`` method on strings can be used to split variables into a list as needed.
- interpreter discovery - The ``auto_legacy`` and ``auto_legacy_silent`` options for ``INTERPRETER_PYTHON`` are deprecated. Use ``auto`` or ``auto_silent`` options instead, as they have the same effect.
- inventory plugins - Setting invalid Ansible variable names in inventory plugins is deprecated.
- oneline callback - The ``oneline`` callback and its associated ad-hoc CLI args (``-o``, ``--one-line``) are deprecated.
- paramiko - The paramiko connection plugin has been deprecated with planned removal in 2.21.
- playbook - The ``timedout.frame`` task result value (injected when a task timeout occurs) is deprecated. Include ``error`` in the ``DISPLAY_TRACEBACK`` config value to capture a full Python traceback for timed out actions.
- playbook syntax - Specifying the task ``args`` keyword without a value is deprecated.
- playbook syntax - Using ``key=value`` args and the task ``args`` keyword on the same task is deprecated.
- playbook syntax - Using a mapping with the ``action`` keyword is deprecated. (https://github.com/ansible/ansible/issues/84101)
- playbook variables - The ``play_hosts`` variable has been deprecated, use ``ansible_play_batch`` instead.
- plugin error handling - The ``AnsibleError`` constructor arg ``suppress_extended_error`` is deprecated. Using ``suppress_extended_error=True`` has the same effect as ``show_content=False``.
- plugins - Accessing plugins with ``_``-prefixed filenames without the ``_`` prefix is deprecated.
- public API - The ``ansible.errors.AnsibleFilterTypeError`` exception type has been deprecated. Use ``AnsibleTypeError`` instead.
- public API - The ``ansible.errors._AnsibleActionDone`` exception type has been deprecated. Action plugins should return a task result dictionary in success cases instead of raising.
- public API - The ``ansible.module_utils.common.json.json_dump`` function is deprecated. Call Python stdlib ``json.dumps`` instead, with ``cls`` set to an Ansible profile encoder type from ``ansible.module_utils.common.json.get_encoder``.
- template lookup - The jinja2_native option is no longer used in the Ansible Core code base. Jinja2 native mode is now the default and only option.
- templating - Support for enabling Jinja2 extensions (not plugins) has been deprecated.
- templating - The ``disable_lookups`` option has no effect, since plugins must be updated to apply trust before any templating can be performed.
- tree callback - The ``tree`` callback and its associated ad-hoc CLI args (``-t``, ``--tree``) are deprecated.

Removed Features (previously deprecated)
----------------------------------------

- Remove deprecated plural form of collection path (https://github.com/ansible/ansible/pull/84156).
- Removed deprecated STRING_CONVERSION_ACTION (https://github.com/ansible/ansible/issues/84220).
- encrypt - passing unsupported passlib hashtype now raises AnsibleFilterError.
- manager - remove deprecated include_delegate_to parameter from get_vars API.
- modules - Modules returning non-UTF8 strings now result in an error. The ``MODULE_STRICT_UTF8_RESPONSE`` setting can be used to disable this check.
- removed deprecated pycompat24 and compat.importlib.
- selector - remove deprecated compat.selector related files (https://github.com/ansible/ansible/pull/84155).
- windows - removed common module functions ``ConvertFrom-AnsibleJson``, ``Format-AnsibleException`` from Windows modules as they are not used and add unneeded complexity to the code.

Security Fixes
--------------

- include_vars action - Ensure that result masking is correctly requested when vault-encrypted files are read. (CVE-2024-8775)
- task result processing - Ensure that action-sourced result masking (``_ansible_no_log=True``) is preserved. (CVE-2024-8775)
- templating - Ansible's template engine no longer processes Jinja templates in strings unless they are marked as coming from a trusted source. Untrusted strings containing Jinja template markers are ignored with a warning. Examples of trusted sources include playbooks, vars files, and many inventory sources. Examples of untrusted sources include module results and facts. Plugins which have not been updated to preserve trust while manipulating strings may inadvertently cause them to lose their trusted status.
- templating - Changes to conditional expression handling removed numerous instances of insecure multi-pass templating (which could result in execution of untrusted template expressions).
- user action won't allow ssh-keygen, chown and chmod to run on existing ssh public key file, avoiding traversal on existing symlinks (CVE-2024-9902).

Bugfixes
--------

- Ansible will now also warn when reserved keywords are set via a module (set_fact, include_vars, etc).
- Ansible will now ensure predictable permissions on remote artifacts, until now it only ensured executable and relied on system masks for the rest.
- Ansible.Basic - Fix ``required_if`` check when the option value to check is unset or set to null.
- Core Jinja test plugins - Builtin test plugins now always return ``bool`` to avoid spurious deprecation warnings for some malformed inputs.
- Correctly return ``False`` when using the ``filter`` and ``test`` Jinja tests on plugin names which are not filters or tests, respectively. (resolves issue https://github.com/ansible/ansible/issues/82084)
- Do not run implicit ``flush_handlers`` meta tasks when the whole play is excluded from the run due to tags specified.
- Errors now preserve stacked error messages even when YAML is involved.
- Fix a display.debug statement with the wrong param in _get_diff_data() method
- Fix disabling SSL verification when installing collections and roles from git repositories. If ``--ignore-certs`` isn't provided, the value for the ``GALAXY_IGNORE_CERTS`` configuration option will be used (https://github.com/ansible/ansible/issues/83326).
- Fix ipv6 pattern bug in lib/ansible/parsing/utils/addresses.py (https://github.com/ansible/ansible/issues/84237)
- Fix returning 'unreachable' for the overall task result. This prevents false positives when a looped task has unignored unreachable items (https://github.com/ansible/ansible/issues/84019).
- Fix templating ``tags`` on plays and roles. (https://github.com/ansible/ansible/issues/69903)
- Implicit ``meta: flush_handlers`` tasks now have a parent block to prevent potential tracebacks when calling methods like ``get_play()`` on them internally.
- Improve performance on large inventories by reducing the number of implicit meta tasks.
- Jinja plugins - Errors raised will always be derived from ``AnsibleTemplatePluginError``.
- Optimize the way tasks from within ``include_tasks``/``include_role`` are inserted into the play.
- Remove use of `required` parameter in `get_bin_path` which has been deprecated.
- Time out waiting on become is an unreachable error (https://github.com/ansible/ansible/issues/84468)
- Update automatic role argument spec validation to not use deprecated syntax (https://github.com/ansible/ansible/issues/85399).
- Use consistent multiprocessing context for action write locks
- Use the requested error message in the ansible.module_utils.facts.timeout timeout function instead of hardcoding one.
- Windows - add support for running on system where WDAC is in audit mode with ``Dynamic Code Security`` enabled.
- YAML parsing - The `!unsafe` tag no longer coerces non-string scalars to strings.
- ``ansible-galaxy`` — the collection dependency resolver now treats version specifiers starting with ``!=`` as unpinned.
- ``package``/``dnf`` action plugins - provide the reason behind the failure to gather the ``ansible_pkg_mgr`` fact to identify the package backend
- action plugins - Action plugins that raise unhandled exceptions no longer terminate playbook loops. Previously, exceptions raised by an action plugin caused abnormal loop termination and loss of loop iteration results.
- ansible-config - format galaxy server configs while dumping in JSON format (https://github.com/ansible/ansible/issues/84840).
- ansible-doc - If none of the files in files exists, path will be undefined and a direct reference will throw an UnboundLocalError (https://github.com/ansible/ansible/pull/84464).
- ansible-doc - fix indentation for first line of descriptions of suboptions and sub-return values (https://github.com/ansible/ansible/pull/84690).
- ansible-doc - fix line wrapping for first line of description of options and return values (https://github.com/ansible/ansible/pull/84690).
- ansible-doc will no longer ignore docs for modules without an extension (https://github.com/ansible/ansible/issues/85279).
- ansible-galaxy - Small adjustments to URL building for ``download_url`` and relative redirects.
- ansible-pull change detection will now work independently of callback or result format settings.
- ansible-test - Disabled the ``bad-super-call`` pylint rule due to false positives.
- ansible-test - Enable the ``sys.unraisablehook`` work-around for the ``pylint`` sanity test on Python 3.11. Previously the work-around was only enabled for Python 3.12 and later. However, the same issue has been discovered on Python 3.11.
- ansible-test - Ensure CA certificates are installed on managed FreeBSD instances.
- ansible-test - Fix Python relative import resolution from ``__init__.py`` files when using change detection.
- ansible-test - Fix incorrect handling of options with optional args (e.g. ``--color``), when followed by other options which are omitted during arg filtering (e.g. ``--docker``). Previously it was possible for non-option arguments to be incorrectly omitted in these cases. (https://github.com/ansible/ansible/issues/85173)
- ansible-test - Fix support for PowerShell module_util imports with the ``-Optional`` flag.
- ansible-test - Fix support for detecting PowerShell modules importing module utils with the newer ``#AnsibleRequires`` format.
- ansible-test - Fix traceback that occurs after an interactive command fails.
- ansible-test - Fix up coverage reporting to properly translate the temporary path of integration test modules to the expected static test module path.
- ansible-test - Fixed traceback when handling certain YAML errors in the ``yamllint`` sanity test.
- ansible-test - Improve type inference for pylint deprecated checks to accommodate some type annotations.
- ansible-test - Managed macOS instances now use the ``sudo_chdir`` option for the ``sudo`` become plugin to avoid permission errors when dropping privileges.
- ansible-test - Updated the ``pylint`` sanity test to skip some deprecation validation checks when all arguments are dynamic.
- ansible-vault will now correctly handle `--prompt`, previously it would issue an error about stdin if no 2nd argument was passed
- ansible_uptime_second - added ansible_uptime_seconds fact support for AIX (https://github.com/ansible/ansible/pull/84321).
- apt_key module - prevent tests from running when apt-key was removed
- async_status module - The ``started`` and ``finished`` return values are now ``True`` or ``False`` instead of ``1`` or ``0``.
- base.yml - deprecated libvirt_lxc_noseclabel config.
- build - Pin ``wheel`` in ``pyproject.toml`` to ensure compatibility with supported ``setuptools`` versions.
- callback plugins - A more descriptive error is now raised if the stdout callback plugin cannot be loaded.
- callback plugins - Callback plugins that do not extend ``ansible.plugins.callback.CallbackBase`` will fail to load with a warning. If the plugin is used as the stdout callback plugin, this will also be a fatal error.
- callback plugins - Removed unused methods - runner_on_no_hosts, playbook_on_setup, playbook_on_import_for_host, playbook_on_not_import_for_host, v2_playbook_on_cleanup_task_start, v2_playbook_on_import_for_host, v2_playbook_on_not_import_for_host.
- callback plugins - The stdout callback plugin is no longer called twice if it is also in the list of additional callback plugins.
- config - Preserve or apply Origin tag to values returned by config.
- config - Prevented fatal errors when ``MODULE_IGNORE_EXTS`` configuration was set.
- config - Templating failures on config defaults now issue a warning. Previously, failures silently returned an unrendered and untrusted template to the caller.
- config - ``ensure_type`` correctly propagates trust and other tags on returned values.
- config - ``ensure_type`` now converts mappings to ``dict`` when requested, instead of returning the mapping.
- config - ``ensure_type`` now converts sequences to ``list`` when requested, instead of returning the sequence.
- config - ``ensure_type`` now correctly errors when ``pathlist`` or ``pathspec`` types encounter non-string list items.
- config - ``ensure_type`` now reports an error when ``bytes`` are provided for any known ``value_type``. Previously, the behavior was undefined, but often resulted in an unhandled exception or incorrect return type.
- config - ``ensure_type`` with expected type ``int`` now properly converts ``True`` and ``False`` values to ``int``. Previously, these values were silently returned unmodified.
- config - various fixes to config lookup plugin (https://github.com/ansible/ansible/pull/84398).
- constructed inventory - Use the ``default_value`` or ``trailing_separator`` in a ``keyed_groups`` entry if the expression result of ``key`` is ``None`` and not just an empty string.
- convert_bool.boolean API conversion function - Unhashable values passed to ``boolean`` behave like other non-boolean convertible values, returning False or raising ``TypeError`` depending on the value of ``strict``. Previously, unhashable values always raised ``ValueError`` due to an invalid set membership check.
- copy - refactor copy module for simplicity.
- copy action now prevents user from setting internal options.
- debconf - set empty password values (https://github.com/ansible/ansible/issues/83214).
- debug - hide loop vars in debug var display (https://github.com/ansible/ansible/issues/65856).
- default callback - Error context is now shown for failing tasks that use the ``debug`` action.
- display - Fix hang caused by early post-fork writers to stdout/stderr (e.g., pydevd) encountering an unreleased fork lock.
- display - The ``Display.deprecated`` method once again properly handles the ``removed=True`` argument (https://github.com/ansible/ansible/issues/82358).
- distro - add support for Linux Mint Debian Edition (LMDE) (https://github.com/ansible/ansible/issues/84934).
- distro - detect Debian as os_family for LMDE 6 (https://github.com/ansible/ansible/issues/84934).
- dnf5 - Handle forwarded exceptions from dnf5-5.2.13 where a generic ``RuntimeError`` was previously raised
- dnf5 - avoid generating excessive transaction entries in the dnf5 history (https://github.com/ansible/ansible/issues/85046)
- dnf5 - fix ``is_installed`` check for packages that are not installed but listed as provided by an installed package (https://github.com/ansible/ansible/issues/84578)
- dnf5 - fix installing a package using ``state=latest`` when a binary of the same name as the package is already installed (https://github.com/ansible/ansible/issues/84259)
- dnf5 - fix traceback when ``enable_plugins``/``disable_plugins`` is used on ``python3-libdnf5`` versions that do not support this functionality
- dnf5 - handle all libdnf5 specific exceptions (https://github.com/ansible/ansible/issues/84634)
- dnf5 - libdnf5 - use ``conf.pkg_gpgcheck`` instead of deprecated ``conf.gpgcheck`` which is used only as a fallback
- dnf5 - matching on a binary can be achieved only by specifying a full path (https://github.com/ansible/ansible/issues/84334)
- dnf5 - when ``bugfix`` and/or ``security`` is specified, skip packages that do not have any such updates, even for new versions of libdnf5 where this functionality changed and it is considered failure
- error handling - Error details and tracebacks from connection and built-in action exceptions are preserved. Previously, much of the detail was lost or mixed into the error message.
- facts - gather pagesize and calculate respective values depending upon architecture (https://github.com/ansible/ansible/issues/84773).
- facts - skip if distribution file path is directory, instead of raising error (https://github.com/ansible/ansible/issues/84006).
- find - skip ENOENT error code while recursively enumerating files. find module will now be tolerant to race conditions that remove files or directories from the target it is currently inspecting. (https://github.com/ansible/ansible/issues/84873).
- first_found lookup - Corrected return value documentation to reflect None (not empty string) for no files found.
- from_yaml_all filter - `None` and empty string inputs now always return an empty list. Previously, `None` was returned in Jinja native mode and empty list in classic mode.
- gather_facts action now defaults to `ansible.legacy.setup` if `smart` was set, no network OS was found and no other alias for `setup` was present.
- gather_facts action will now issues errors and warnings as appropriate if a network OS is detected but no facts modules are defined for it.
- gather_facts action, will now add setup when 'smart' appears with other modules in the FACTS_MODULES setting (#84750).
- get_url - add a check to recognize incomplete data transfers.
- get_url - add support for BSD-style checksum digest file (https://github.com/ansible/ansible/issues/84476).
- get_url - fix honoring ``filename`` from the ``content-disposition`` header even when the type is ``inline`` (https://github.com/ansible/ansible/issues/83690)
- host_group_vars - fixed defining the 'key' variable if the get_vars method is called with cache=False (https://github.com/ansible/ansible/issues/84384)
- include_tasks - fix templating options when used as a handler (https://github.com/ansible/ansible/pull/85015).
- include_vars - fix including previously undefined hash variables with hash_behaviour merge (https://github.com/ansible/ansible/issues/84295).
- iptables - Allows the wait parameter to be used with iptables chain creation (https://github.com/ansible/ansible/issues/84490)
- linear strategy - fix executing ``end_role`` meta tasks for each host, instead of handling these as implicit run_once tasks (https://github.com/ansible/ansible/issues/84660).
- local connection plugin - Become timeout errors now include all received data. Previously, the most recently-received data was discarded.
- local connection plugin - Ensure ``become`` success validation always occurs, even when an active plugin does not set ``prompt``.
- local connection plugin - Fixed cases where the internal ``BECOME-SUCCESS`` message appeared in task output.
- local connection plugin - Fixed hang or spurious failure when data arrived concurrently on stdout and stderr during a successful ``become`` operation validation.
- local connection plugin - Fixed hang when a become plugin expects a prompt but a password was not provided.
- local connection plugin - Fixed hang when an active become plugin incorrectly signals lack of prompt.
- local connection plugin - Fixed hang when an internal become read timeout expired before the password prompt was written.
- local connection plugin - Fixed hang when only one of stdout or stderr was closed by the ``become_exe`` subprocess.
- local connection plugin - Fixed long timeout/hang for ``become`` plugins that repeat their prompt on failure (e.g., ``sudo``, some ``su`` implementations).
- local connection plugin - Fixed silent ignore of ``become`` failures and loss of task output when data arrived concurrently on stdout and stderr during ``become`` operation validation.
- local connection plugin - Fixed task output header truncation when post-become data arrived before ``become`` operation validation had completed.
- local connection plugin - The command-line used to create subprocesses is now always ``str`` to avoid issues with debuggers and profilers.
- lookup plugins - The ``terms`` arg to the ``run`` method is now always a list. Previously, there were cases where a non-list could be received.
- module arg templating - When using a templated raw task arg and a templated ``args`` keyword, args are now merged. Previously use of templated raw task args silently ignored all values from the templated ``args`` keyword.
- module defaults - Module defaults are no longer templated unless they are used by a task that does not override them. Previously, all module defaults for all modules were templated for every task.
- module respawn - limit to supported Python versions
- package_facts module when using 'auto' will return the first package manager found that provides an output, instead of just the first one, as this can be foreign and not have any packages.
- password lookup - fix acquiring the lock when human-readable FileExistsError error message is not English.
- plugin loader - A warning is now emitted for any plugin which fails to load due to a missing base class.
- plugin loader - Apply template trust to strings loaded from plugin configuration definitions and doc fragments.
- psrp - Improve stderr parsing when running raw commands that emit error records or stderr lines.
- regex_search filter - Corrected return value documentation to reflect None (not empty string) for no match.
- respawn - use copy of env variables to update existing PYTHONPATH value (https://github.com/ansible/ansible/issues/84954).
- runas become - Fix up become logic to still get the SYSTEM token with the most privileges when running as SYSTEM.
- sequence lookup - sequence query/lookups without positional arguments now return a valid list if their kwargs comprise a valid sequence expression (https://github.com/ansible/ansible/issues/82921).
- service_facts - skip lines which does not contain service names in openrc output (https://github.com/ansible/ansible/issues/84512).
- ssh - Improve the logic for parsing CLIXML data in stderr when working with Windows host. This fixes issues when the raw stderr contains invalid UTF-8 byte sequences and improves embedded CLIXML sequences.
- ssh - Raise exception when sshpass returns error code (https://github.com/ansible/ansible/issues/58133).
- ssh - connection options were incorrectly templated during ``reset_connection`` tasks (https://github.com/ansible/ansible/pull/84238).
- ssh agent - Fixed several potential startup hangs for badly-behaved or overloaded ssh agents.
- ssh connection plugin - Allow only one password prompt attempt when utilizing ``SSH_ASKPASS`` (https://github.com/ansible/ansible/issues/85359)
- stability - Fixed silent process failure on unhandled IOError/OSError under ``linear`` strategy.
- su become plugin - Ensure generated regex from ``prompt_l10n`` config values is properly escaped.
- su become plugin - Ensure that password prompts are correctly detected in the presence of leading output. Previously, this case resulted in a timeout or hang.
- su become plugin - Ensure that trailing colon is expected on all ``prompt_l10n`` config values.
- sudo become plugin - The `sudo_chdir` config option allows the current directory to be set to the specified value before executing sudo to avoid permission errors when dropping privileges.
- sunos - remove hard coding of virtinfo command in facts gathering code (https://github.com/ansible/ansible/pull/84357).
- task timeout - Specifying a negative task timeout now results in an error.
- template action - Template files where the entire file's output renders as ``None`` are no longer emitted as the string "None", but instead render to an empty file as in previous releases.
- templating - Fixed cases where template expression blocks halted prematurely when a Jinja macro invocation returned an undefined value.
- templating - Jinja macros returned from a template expression can now be called from another template expression.
- to_yaml/to_nice_yaml filters - Eliminated possibility of keyword arg collisions with internally-set defaults.
- unarchive - Clamp timestamps from beyond y2038 to representible values when unpacking zip files on platforms that use 32-bit time_t (e.g. Debian i386).
- uri - Form location correctly when the server returns a relative redirect (https://github.com/ansible/ansible/issues/84540)
- uri - Handle HTTP exceptions raised while reading the content (https://github.com/ansible/ansible/issues/83794).
- uri - mark ``url`` as required (https://github.com/ansible/ansible/pull/83642).
- user - Create Buildroot subclass as alias to Busybox (https://github.com/ansible/ansible/issues/83665).
- user - Set timeout for passphrase interaction.
- user - Update prompt for SSH key passphrase (https://github.com/ansible/ansible/issues/84484).
- user - Use higher precedence HOME_MODE as UMASK for path provided (https://github.com/ansible/ansible/pull/84482).
- user action will now require O(force) to overwrite the public part of an ssh key when generating ssh keys, as was already the case for the private part.
- user module now avoids changing ownership of files symlinked in provided home dir skeleton
- variables - Added Jinja scalar singletons (``true``, ``false``, ``none``) to invalid Ansible variable name detection. Previously, variables with these names could be assigned without error, but could not be resolved.
- vars lookup - The ``default`` substitution only applies when trying to look up a variable which is not defined. If the variable is defined, but templates to an undefined value, the ``default`` substitution will not apply. Use the ``default`` filter to coerce those values instead.
- wait_for_connection - a warning was displayed if any hosts used a local connection (https://github.com/ansible/ansible/issues/84419)
