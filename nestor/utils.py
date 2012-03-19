import os
import tempfile

from fabric.api import sudo, run, settings, hide, abort, put
from fabric.contrib.files import exists


def upload_template(filename, destination, context=None, use_jinja=False,
    template_dir=None, use_sudo=False, backup=True, mirror_local_mode=False,
    mode=None):
    """
    Render and upload a template text file to a remote host.

    ``filename`` should be the path to a text file, which may contain `Python
    string interpolation formatting
    <http://docs.python.org/release/2.5.4/lib/typesseq-strings.html>`_ and will
    be rendered with the given context dictionary ``context`` (if given.)

    Alternately, if ``use_jinja`` is set to True and you have the Jinja2
    templating library available, Jinja will be used to render the template
    instead. Templates will be loaded from the invoking user's current working
    directory by default, or from ``template_dir`` if given.

    The resulting rendered file will be uploaded to the remote file path
    ``destination``.  If the destination file already exists, it will be
    renamed with a ``.bak`` extension unless ``backup=False`` is specified.

    By default, the file will be copied to ``destination`` as the logged-in
    user; specify ``use_sudo=True`` to use `sudo` instead.

    The ``mirror_local_mode`` and ``mode`` kwargs are passed directly to an
    internal `~fabric.operations.put` call; please see its documentation for
    details on these two options.

    .. versionchanged:: 1.1
        Added the ``backup``, ``mirror_local_mode`` and ``mode`` kwargs.
    """
    func = use_sudo and sudo or run
    # Normalize destination to be an actual filename, due to using StringIO
    with settings(hide('everything'), warn_only=True):
        if func('test -d %s' % destination).succeeded:
            sep = "" if destination.endswith('/') else "/"
            destination += sep + os.path.basename(filename)

    # Use mode kwarg to implement mirror_local_mode, again due to using
    # StringIO
    if mirror_local_mode and mode is None:
        mode = os.stat(filename).st_mode
        # To prevent put() from trying to do this
        # logic itself
        mirror_local_mode = False

    # Process template
    text = None
    if use_jinja:
        try:
            from jinja2 import Environment, FileSystemLoader
            jenv = Environment(loader=FileSystemLoader(template_dir or '.'))
            text = jenv.get_template(filename).render(**context or {})
        except ImportError:
            import traceback
            tb = traceback.format_exc()
            abort(tb + "\nUnable to import Jinja2 -- see above.")
    else:
        with open(filename) as inputfile:
            text = inputfile.read()
        if context:
            text = text % context

    # Back up original file
    if backup and exists(destination):
        func("cp %s{,.bak}" % destination)

    with tempfile.TemporaryFile() as tmp:
        tmp.write(text.encode('utf-8'))
        # Upload the file.
        put(
            local_path=tmp,
            remote_path=destination,
            use_sudo=use_sudo,
            mirror_local_mode=mirror_local_mode,
            mode=mode
        )
