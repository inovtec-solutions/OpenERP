#!/usr/bin/env python

""" mx.Misc.Daemon - Tools to start and stop server processes.

    WARNING: This module is still experimental and likely to
             change its API between releases.

    Copyright (c) 2008-2011, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import sys, os, signal, time, socket
from mx import Tools, Log

### Globals

__version__ = '0.5.0'

_debug = 1

### Errors

class Error(StandardError):
    pass

class ServerAlreadyRunningError(Error):
    pass

class ProcessNotStoppedError(Error):
    pass

class ServerNotStartedError(Error):
    pass

class ServerNotStoppedError(ProcessNotStoppedError):
    pass

class WorkerNotStartedError(Error):
    pass

class WorkerNotStoppedError(ProcessNotStoppedError):
    pass

### Helpers

def kill_process(pid,
                 force=True, default_exit_status=-1,
                 shutdown_time=0.1, kill_time=0.1,
                 log=Log.log, log_prefix=''):

    """ Kill a process pid and collect it.

        Returns the process exit status or default_exit_status in
        case this cannot be determined.

        Sends the process a SIGTERM signal and waits shutdown_time
        seconds for it to terminate.

        If force is true (default), the process is sent a SIGKILL
        signal if it doesn't terminate after sending the SIGTERM.  The
        function will then wait another kill_time seconds for the
        process to end.

        Raises a ProcessNotStoppedError in case the process cannot be
        terminated.

        log may be set to a mx.Log instance. It defaults to the
        mx.Log.log instance. log_prefix is prefixed to the log
        messages.

    """
    # Stop the worker process using SIGTERM
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError, reason:
        log.exception(log.ERROR,
                      '%sError stopping worker process with PID %s',
                      log_prefix,
                      pid)
        return default_exit_status

    # Wait .worker_shutdown_time seconds until the server has
    # stopped
    cstatus = default_exit_status
    for i in xrange(int(shutdown_time * 100) + 1):
        try:
            cpid, cstatus = os.waitpid(pid, os.WNOHANG)
        except OSError, reason:
            # Process has already terminated
            if _debug:
                log(log.DEBUG,
                    '%sProcess PID %s already terminated',
                    log_prefix,
                    pid)
            return cstatus
        if cpid == pid:
            if _debug:
                log(log.DEBUG,
                    '%sProcess PID %s collected with exit status %s',
                    log_prefix,
                    pid,
                    cstatus)
            return cstatus
        time.sleep(0.01)

    if force:
        # Kill the worker process using SIGKILL
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError, reason:
            log.exception(
                log.ERROR,
                '%sError killing worker process with PID %s',
                log_prefix,
                pid)

        # Wait .worker_kill_time to collect it
        for i in xrange(int(kill_time * 100) + 1):
            try:
                cpid, cstatus = os.waitpid(pid, os.WNOHANG)
            except OSError, reason:
                # Process has already terminated
                if _debug:
                    log(log.DEBUG,
                        '%sProcess PID %s already terminated '
                        'after SIGKILL',
                        log_prefix,
                        pid)
                return cstatus
            if cpid == pid:
                if _debug:
                    log(log.DEBUG,
                        '%sProcess PID %s collected with exit status %s '
                        'after SIGKILL',
                        log_prefix,
                        pid,
                        cstatus)
                return cstatus
            time.sleep(0.01)

    # Did not work out...
    if _debug:
        log(log.DEBUG,
            '%sProcess PID %s could not be killed',
            log_prefix,
            pid)
    raise ProcessNotStoppedError(
        'Process with PID %s did not stop' % pid)

### Single-process Daemon

class ServerDaemon(object):

    """ Server daemon encapsulation.

        This class provides an easy way to setup a Unix server daemon
        that uses a single process. It may still spawn off additional
        processes, but this encapsulation only manages the main
        process.

        The implementation runs two contexts:

        - the control context in which .start_server() and .stop_server()
          are called

        - the server process contect in which .main() is run

    """
    # Name of the server
    name = 'Server Daemon'

    # PID of the process
    pid = 0

    # Location of the PID file of the parent process
    pid_file = 'server.pid'

    # umask to set for the forked server process
    umask = 022

    # Root dir to change to for the forked server process
    root_dir = ''

    # Range of file descriptors to close after the fork; all open fds
    # except of stdin, stdout, stderr
    close_file_descriptors = tuple(range(3, 99))

    # mxLog object to use
    log = Log.log

    # Log id to use in the forked server process
    log_id = ''

    # Process name to use for the forked server process. Note: this is
    # not guaranteed to work
    process_name = ''

    # Server startup time in seconds. The .start_server()
    # method will wait at most this number of seconds for the main
    # server process to initialize and enter the .main() method. This
    # includes forking overhead, module import times, etc. It does not
    # cover the startup time that the server may need to become usable
    # for external applications.  The startup time can be configured
    # with .server_startup_time
    server_startup_time = 2

    # Startup initialization time of the server in seconds. The
    # .start_server() method will unconditionally wait this number of
    # seconds after having initialized the server in order to give the
    # .main() method a chance to setup any resources it may need to
    # initialize.
    server_startup_init_time = 0

    # Server shutdown time in seconds. The .stop_server()
    # method will wait at most this number of seconds for the main
    # server process to terminate after sending it a TERM signal.
    server_shutdown_time = 2

    # Kill time of the server processes in seconds. The .stop_server()
    # method will wait this number of second for the worker processes
    # to terminate after having received the KILL signal.
    server_kill_time = 1

    # Shutdown cleanup time of the server in seconds. The
    # .stop_server() method will unconditionally wait this number of
    # seconds after having terminated the main server process in order
    # to give possibly additionally spawned processes a chance to
    # terminate cleanly as well.
    server_shutdown_cleanup_time = 0

    ###
    
    def setup_server(self, **parameters):

        """ Prepare the server startup and adjust the parameters to be
            passed on to the server's .main() method.

            This method is called by .start_server() before forking
            off a child process in order to give the WorkerProcess
            implementation a chance to adjust itself to the
            parameters.

            It has to return a copy of the parameters keyword argument
            dictionary.

            This method is called in the context of the server.

        """
        return parameters.copy()

    def _kill_server(self, pid):

        """ Kill a server process pid and collect it.

            Returns the process exit status or -1 in case this cannot
            be determined.

            Raises a ServerNotStoppedError in case the process cannot
            be stopped.

        """
        try:
            return kill_process(
                pid,
                shutdown_time=self.server_shutdown_time,
                kill_time=self.server_kill_time,
                log=self.log,
                log_prefix='%s: ' % self.name)
        except ProcessNotStoppedError:
            # Did not work out...
            raise ServerNotStoppedError(
                '%s: Server process with PID %s did not stop' % (
                self.name,
                    pid))

    def start_server(self, **parameters):

        """ Starts the server.

            Keyword parameters are passed on to the forked process'
            .main() method.

            Returns the PID of the started server daemon.

            Raises a ServerAlreadyRunningError if the server is
            already running.  Raises a ServerNotStartedError in case
            the daemon could not be started.

        """

        # Verify if we have a running server process
        pid = self.server_status()
        if pid is not None:
            raise ServerAlreadyRunningError(
                'Server is already running (PID %s)' % pid)

        # Prepare startup
        parameters = self.setup_server(**parameters)
        assert parameters is not None, \
               '.setup_server() did not return a parameters dictionary'

        # Flush the standard file descriptors
        sys.stderr.flush()
        sys.stdout.flush()

        # Fork a child process, errors will be reported to the caller
        pid = os.fork()
        if pid != 0:
            
            ### Parent process

            # Collect the first child
            if _debug:
                self.log(
                    self.log.DEBUG,
                    '%s: '
                    'Waiting for the first child with PID %s to terminate',
                    self.name,
                    pid)
            os.waitpid(pid, 0)

            # Wait a few seconds until the server has started
            if _debug:
                self.log(
                    self.log.DEBUG,
                    '%s: '
                    'Waiting for the server process to startup',
                    self.name)
            for i in xrange(int(self.server_startup_time * 100) + 1):
                spid = self.server_status()
                if spid is not None:
                    break
                time.sleep(0.01)
            else:
                # Server did not startup in time: terminate the first
                # child
                self.log(self.log.ERROR,
                         '%s: Server process failed to startup',
                         self.name)
                try:
                    self._kill_server(pid)
                except ServerNotStoppedError:
                    pass
                # Report the problem; XXX Note that the second child
                # may still startup after this first has already
                # terminated.
                raise ServerNotStartedError(
                    '%s did not start up' % self.name)
            if self.server_startup_init_time:
                time.sleep(self.server_startup_init_time)
            return spid

        ### This is the first child process

        # Daemonize process
        os.setpgrp()
        if self.root_dir:
            os.chdir(self.root_dir)
        if self.umask:
            os.umask(self.umask)
        try:
            # Try to become a session leader
            os.setsid()
        except OSError:
            # We are already the process session leader
            pass

        # Close all open fds except of stdin, stdout, stderr
        self.log.close()
        for i in self.close_file_descriptors:
            try:
                os.close(i)
            except (IOError, OSError), reason:
                pass

        # Fork again to become a separate daemon process
        pid = os.fork()
        if pid != 0:
            # We need to terminate the "middle" process at this point, since we
            # don't want to continue with two instances of the original caller.
            # We must not call any cleanup handlers here.
            os._exit(0)

        ### This is the second child process: the server daemon

        # Turn the daemon into a process group leader
        os.setpgrp()

        # Reopen the log file
        self.log.open()
        if self.log_id:
            self.log.setup(log_id=self.log_id)

        # Redirect stdout and stderr to the log file
        self.log.redirect_stdout()
        self.log.redirect_stderr()

        # Try to rename the process
        if self.process_name:
            try:
                Tools.setproctitle(self.process_name)
            except AttributeError:
                pass

        # Save the PID of the server daemon process
        self.pid = os.getpid()
        self.save_server_pid(self.pid)

        # We need to remove the PID file on exit
        rc = 0
        try:
            try:
                self.log(
                    self.log.INFO,
                    '%s: Server process PID %s %s',
                    self.name,
                    self.pid,
                    '*' * 60)

                # Run the server's .main() method
                main_rc = self.main(**parameters)
                
                # Return the exit code, if it's an integer
                if main_rc is not None and isinstance(main_rc, int):
                    rc = main_rc
                
            except SystemExit, exc:
                # Normal shutdown
                rc = exc.code
                self.log(self.log.INFO,
                         '%s: Shutting down with status: %s',
                         self.name,
                         rc)

            except Exception:
                # Something unexpected happened... log the problem and exit
                self.log.traceback(self.log.ERROR,
                                   '%s: Unexpected server error:',
                                   self.name)
                rc = 1
                
        finally:
            # Remove the PID file, if it still exists and points to
            # this server process.
            current_pid = self.get_server_pid()
            if current_pid is not None and current_pid == os.getpid():
                self.remove_server_pid_file()

        # Exit process
        if os.getpid() != self.pid:
            # PID changed, so better not run finalizations
            os._exit(rc)
        else:
            # Normal exit
            sys.exit(rc)

    def stop_server(self):

        """ Stops the server

            Returns the PID of the stopped server or None in case the
            server could not be stopped or no longer ran.

        """
        # Retrieve the PID of the currently running server process
        pid = self.get_server_pid()
        if pid is None:
            return

        # Stop the server process
        try:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, reason:
                self.log.exception(self.log.ERROR,
                                   '%s: Error stopping server',
                                   self.name)
                return

            # Wait a few seconds until the server has stopped
            for i in xrange(int(self.server_shutdown_time * 100) + 1):
                try:
                    cpid, cstatus = os.waitpid(pid, os.WNOHANG)
                except OSError, reason:
                    # Process has already terminated
                    break
                if cpid == pid:
                    if _debug:
                        log(log.DEBUG,
                            '%s: Collected PID %s with exit status %s',
                            self.name,
                            pid,
                            cstatus)
                    break
                time.sleep(0.01)
            else:
                raise ServerNotStoppedError(
                    '%s did not stop' % self.name)
            if self.server_shutdown_cleanup_time:
                time.sleep(self.server_shutdown_cleanup_time)
            return pid

        finally:
            # Remove the PID file, if it still exists and points to
            # the server process we just terminated.
            current_pid = self.get_server_pid()
            if current_pid is not None and current_pid == os.getpid():
                self.remove_server_pid_file()

    def server_status(self):

        """ Returns the PID of a running server or None in case no
            server is found to be running.

            The check is based on the contents of the PID file.  It
            won't be able to detect the server any more if the PID
            file is removed.

        """
        # Get the server's PID
        pid = self.get_server_pid()
        if pid is None:
            return pid

        # Is that process still running?
        try:
            os.getpgid(pid)
        except OSError:
            return None
        return pid

    ### PID management

    def get_server_pid(self):

        """ Returns the PID of the server or None if we don't have a PID file

        """
        try:
            f = open(self.pid_file, 'rb')
            try:
                return int(f.read().strip())
            finally:
                f.close()
        except (OSError, IOError, ValueError), reason:
            if _debug > 1:
                self.log(
                    self.log.DEBUG,
                    '%s: Could not find the server PID file %s: %s',
                    self.name,
                    self.pid_file,
                    reason)
            return None

    def save_server_pid(self, pid):

        """ Saves the PID of the server into a PID file
        
        """
        f = open(self.pid_file, 'wb')
        try:
            f.write('%s\n' % pid)
            f.flush()
        finally:
            f.close()

    def remove_server_pid_file(self):

        """ Remove the PID file

        """
        try:
            os.remove(self.pid_file)
        except (OSError, IOError):
            pass
        else:
            if _debug:
                self.log(
                    self.log.DEBUG,
                    '%s: Removed the server PID file %s',
                    self.name,
                    self.pid_file)

    ### Main entry point for the server context

    def main(self, **parameters):

        """ Main method of the server process.

            parameters is a dictionary passed in from the control
            script and contains optional parameters for the server.

        """
        pass

### Multiple-process Server Daemon

class WorkerServerDaemon(ServerDaemon):

    """ Server daemon that spawns off additional worker processes.

        This implementation runs a single administration process which
        then spawns off a fixed number of additional worker processes
        to do the actual work. The worker processes are encapsulated
        by the WorkerProcess class.

        Unlike for ServerDaemon, the .main() method of the
        WorkerServerDaemon may not be overridden, since this
        implements the worker management loop of the daemon.

        Instead, the WorkerProcess.main() method has to be overridden
        to provide functionality to the workers.

    """
    # Dictionary of active WorkerProcess instances
    workers = None

    # WorkerProcess class to use; defaults to WorkerProcess if not set.
    WorkerProcess = None

    # Number of worker processes to keep running
    max_workers = 5

    # Check interval in seconds
    check_interval = 5

    # Time to wait between initial worker process forks in seconds
    initial_startup_interval = 0

    def main(self, **parameters):

        """ Start up .max_workers worker processes and monitor
            them until the server gets a SIGTERM signal.

            If a worker process shuts down, the server will
            automatically startup a new replacement.

            This check is done every .check_interval seconds and only
            one new worker started by check interval to avoid
            overloading the server machine.
            
        """
        # Initialize work variables
        self.workers = {}
        if self.WorkerProcess is None:
            self.WorkerProcess = WorkerProcess

        # Add SIGTERM signal handler
        signal.signal(signal.SIGTERM, self.sigterm_handler)

        try:
            try:
                # Startup .max_workers worker processes
                for i in xrange(self.max_workers):
                    self.spawn_worker(**parameters)
                    time.sleep(self.initial_startup_interval)

                # Enter end-less management loop
                while True:
                    self.check_workers()
                    start_new_workers = self.max_workers - len(self.workers)
                    if start_new_workers:
                        for i in xrange(start_new_workers):
                            self.spawn_worker(**parameters)
                    self.idle_tasks()
                    time.sleep(self.check_interval)

            except SystemExit:

                # Remove the signal handler
                signal.signal(signal.SIGTERM, signal.SIG_IGN)

                # Stop all workers
                self.stop_workers()

                # Reraise
                raise

        finally:
            # Remove the signal handler
            signal.signal(signal.SIGTERM, signal.SIG_IGN)

            # Try a fast worker shutdown, if there are managed workers
            # left
            if self.workers:
                self.terminate_workers()

    def idle_tasks(self):

        """ Method called before going idle until the next check
            interval.

        """
        pass

    def sigterm_handler(self, signal_number, frame):

        """ SIGTERM signal handler that converts the signal into
            a SystemExit exception.

        """
        self.log(self.log.INFO,
                 '%s: Received SIGTERM - shutting down',
                 self.name)
        raise SystemExit(0)

    def check_workers(self):

        """ Check all currently managed worker processes, collect
            terminated ones and update the management dictionary .workers.

        """
        for pid, worker_process in self.workers.items():

            # Check whether the process still exists
            if worker_process.worker_status():

                # Check whether it is still running, if not, collect it
                try:
                    cpid, cstatus = os.waitpid(pid, os.WNOHANG)

                except OSError, reason:
                    # No longer alive
                    self.log(self.log.ERROR,
                             '%s: Worker %r shut down unexpectedly: %s',
                             self.name,
                             worker_process,
                             reason)
                    worker_process.worker_exited(-1)

                else:
                    if cpid == 0:
                        # Everything ok
                        if _debug > 1:
                            self.log(self.log.DEBUG,
                                     '%s: Worker %r is alive',
                                     self.name,
                                     worker_process)
                        continue
                    
                    elif pid == cpid:
                        # The correct child process was collected
                        self.log(self.log.INFO,
                                 '%s: Worker %r shut down with status: %s',
                                 self.name,
                                 worker_process,
                                 cstatus)
                        worker_process.worker_exited(cstatus)

                    else:
                        # Some other process was collected
                        self.log(self.log.ERROR,
                                 '%s: Collected worker process PID %s '
                                 'with status: %s',
                                 self.name,
                                 cpid,
                                 cstatus)
                        continue

            # Remove from management dictionary
            del self.workers[pid]

    def terminate_workers(self):

        """ Send a SIGTERM to all worker processes.

            This is a fast way of terminating all child processes
            meant to be used during server shutdown.

        """
        self.log(self.log.INFO,
                 '%s: Terminating worker processes',
                 self.name)

        # First round: send SIGTERM to all children
        for pid, worker_process in self.workers.items():

            # Remove dead processes directly
            if not worker_process.worker_status():
                del self.workers[pid]
                continue
        
            # Send SIGTERM
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

        # Second round: collect children
        for pid, worker_process in self.workers.items():

            # Remove management entry
            del self.workers[pid]

            # Skip dead processes directly
            if not worker_process.worker_status():
                continue

            # Collect the child
            try:
                cpid, cstatus = os.waitpid(pid, os.WNOHANG)
            except OSError:
                # Ignore errors
                pass

    def stop_workers(self):

        """ Slow, but clean method of shutting down worker processes.

            This version waits for each child process to shut down
            nicely.

        """
        self.log(self.log.INFO,
                 '%s: Shutting down the worker processes',
                 self.name)
        
        for pid, worker_process in self.workers.items():
            try:
                worker_process.stop_worker()
            except WorkerNotStoppedError, reason:
                # Ignore errors
                pass

            # Remove management entry
            del self.workers[pid]

    def spawn_worker(self, **parameters):

        """ Spawn a new worker child process.

        """
        # Start new .WorkerProcess
        worker_process = self.WorkerProcess(self)
        parameters = self.prepare_worker_startup(worker_process,
                                                 **parameters)
        assert parameters is not None, \
               '.prepare_worker_startup() did not return a parameters dictionary'
        try:
            worker_process.start_worker(**parameters)
        except WorkerNotStartedError, reason:
            self.log(self.log.ERROR,
                     '%s: Failed to start a new worker process: %s',
                     self.name,
                     reason)
            return

        # Add to dictionary
        self.workers[worker_process.pid] = worker_process
        self.log(self.log.INFO,
                 '%s: Spawned new worker process %r',
                 self.name,
                 worker_process)
        return worker_process.pid

    def prepare_worker_startup(self, worker_process, **parameters):

        """ Prepare the worker startup by the server.

            This method must return a copy of the parameters keyword
            dictionary which is to be used by the server to start the
            worker.

            The method is called prior to calling .start_worker() on
            the worker_process.

            The default implementation returns a shallow copy of the
            startup parameters dictionary.

        """
        return parameters.copy()

### Worker process class

class WorkerProcess(object):

    """ Worker process encapsulation.

        These work a lot like server processes, except that they are
        managed by daemon process as child processes.

        The implementation uses two contexts:

        - the server daemon context in which .start_server() and
          .stop_server() are called

        - the worker process contect in which .main() is run

        The .main() method has to be overridden to implement the
        worker process logic.

    """
    # Note: This code is similar to ServerDaemon, but for worker
    # processes we don't fork twice since we want the workers to be
    # child processes of the server process.

    # Name of the worker
    name = 'Worker Process'

    # PID of the worker process; set in both the server and the worker
    # process context
    pid = 0

    # Started flag. Set by .start_worker()/.stop_worker() in the
    # server context.
    started = False

    # Exit status code. Set by .worker_exited() in the server context.
    exit_status = 0

    # mxLog object to use. Inherited from the ServerDaemon if None
    log = None

    # Log id to use in the worker process. Inherited from the
    # ServerDaemon if None
    log_id = None

    # Process name to use for the worker process. Note: this is not
    # guaranteed to work. Inherited from the ServerDaemon if None
    process_name = None

    # Startup time of the worker processes in seconds. The
    # .start_worker() method will wait this number of second for the
    # worker process to start up.
    worker_startup_time = 2

    # Shutdown time of the worker processes in seconds. The
    # .stop_worker() method will wait this number of second for the
    # worker processes to terminate.
    worker_shutdown_time = 2

    # Kill time of the worker processes in seconds. The .stop_worker()
    # method will wait this number of second for the worker processes
    # to terminate after having received the KILL signal.
    worker_kill_time = 1

    # Range of file descriptors to close after the fork; all open fds
    # except of stdin, stdout, stderr
    close_file_descriptors = tuple(range(3, 99))

    def __init__(self, server_daemon):

        # Inherit settings from the server
        if self.log is None:
            self.log = server_daemon.log
        if self.log is None:
            self.log = Log.LogNothing
        if self.log_id is None:
            self.log_id = server_daemon.log_id
        if self.process_name is None:
            self.process_name = server_daemon.process_name

    def __repr__(self):

        return '%s(%s with PID %s)' % (
            self.__class__.__name__,
            self.name,
            self.pid)

    def setup_worker(self, **parameters):

        """ Prepare the worker startup and adjust the parameters to be
            passed on to the worker's .main() method.

            This method is called by .start_worker() before forking
            off a child process in order to give the WorkerProcess
            implementation a chance to adjust itself to the
            parameters.

            It has to return a copy of the parameters keyword argument
            dictionary.

            This method is called in the context of the server.

        """
        return parameters.copy()

    def start_worker(self, **parameters):

        """ Start the worker process and pass the given keyword parameters
            to the .main() method.

        """
        # Prepare startup
        parameters = self.setup_worker(**parameters)
        assert parameters is not None, \
               '.setup_worker() did not return a parameters dictionary'

        # Flush file descriptors
        sys.stderr.flush()
        sys.stdout.flush()

        # Create a socket pair
        server_socket, worker_socket = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_STREAM)

        # Fork a child process, errors will be reported to the caller
        pid = os.fork()
        if pid != 0:

            ### Server process context ...

            # Close our end of the socket pair
            server_socket.close()

            # Wait for the child to start up
            worker_socket.settimeout(self.worker_startup_time)
            try:
                ok = worker_socket.recv(1)
            except socket.timeout:
                ok = None
            worker_socket.close()
            if not ok:
                # Terminate the child, if it didn't startup in time
                self.log(
                    self.log.ERROR,
                    '%s: '
                    'Collecting worker process PID %s due to startup failure',
                    self.name,
                    pid)
                try:
                    self._kill_worker(pid)
                except WorkerNotStoppedError:
                    pass
                
                # Report the failure
                raise WorkerNotStartedError(
                    '%s: Worker process with PID %s did not start up' % (
                        self.name,
                        pid))

            # Remember the worker process pid and return it
            self.pid = pid
            self.started = True
            self.exit_status = 0
            return pid

        ### Worker process context ...

        # Close our end of the socket pair
        worker_socket.close()

        # Close all open fds except of stdin, stdout, stderr
        self.log.close()
        server_socket_fd = server_socket.fileno()
        for i in self.close_file_descriptors:
            if i == server_socket_fd:
                # We'll close that manually later on
                continue
            try:
                os.close(i)
            except (IOError, OSError), reason:
                pass

        # Reopen the log file
        self.log.open()
        if self.log_id:
            self.log.setup(log_id=self.log_id)

        # Redirect stdout and stderr to the log file
        self.log.redirect_stdout()
        self.log.redirect_stderr()

        # Try to rename the process
        if self.process_name:
            try:
                Tools.setproctitle(self.process_name)
            except AttributeError:
                pass

        # Set the PID of the worker process
        self.pid = os.getpid()

        # Let the server process know that we've started up
        server_socket.send('1')
        server_socket.close()

        # Run the .main() method
        rc = 0
        try:
            try:
                self.log(self.log.INFO,
                         '%s: Worker process PID %s %s',
                         self.name,
                         self.pid,
                         '-' * 40)
                if _debug > 1:
                    self.log.object(
                        self.log.DEBUG,
                        '%s: Using the following startup parameters:' %
                        self.name,
                        parameters)

                # Run the worker's .main() method
                main_rc = self.main(**parameters)

                # Return the exit code, if it's an integer
                if main_rc is not None and isinstance(main_rc, int):
                    rc = main_rc
                
            except Exception:
                # Something unexpected happened... log the problem and exit
                self.log.traceback(self.log.ERROR,
                                   '%s: '
                                   'Unexpected worker process error:',
                                   self.name)
                rc = 1

        finally:
            self.cleanup_worker()

        # Exit process
        os._exit(rc)

    def _kill_worker(self, pid):

        """ Kill a worker process pid and collect it.

            Returns the process exit status or -1 in case this cannot
            be determined.

            Raises a WorkerNotStoppedError in case the process cannot
            be stopped.

        """
        try:
            return kill_process(
                pid,
                shutdown_time=self.worker_shutdown_time,
                kill_time=self.worker_kill_time,
                log=self.log,
                log_prefix='%s: ' % self.name)
        except ProcessNotStoppedError:
            # Did not work out...
            raise WorkerNotStoppedError(
                '%s: Worker process with PID %s did not stop' % (
                self.name,
                    pid))

    def stop_worker(self):

        """ Stop the worker child process.

        """
        # Check if the worker process is still running
        if not self.worker_status():
            self.log(self.log.ERROR,
                     '%s: Worker process with PID %s is no longer running',
                     self.name,
                     self.pid)
            return

        # Stop the worker process
        pid = self.pid
        cstatus = self._kill_worker(pid)
        self.worker_exited(cstatus or -1)
        return pid

    def worker_status(self):

        """ Returns the PID of the running worker process or None in
            case no worker process is found to be running.

        """
        # Is the worker process still running?
        try:
            os.getpgid(self.pid)
        except OSError:
            self.worker_exited()
            return None
        return self.pid

    def worker_exited(self, status=-1):

        """ Called in case the worker has exited.

            status gives the exit code.

        """
        self.started = False
        self.exit_status = status

    def cleanup_worker(self):

        """ This method is called on worker process exit to cleanup
            before exiting the process.

            It is run in the context of the worker process.

        """
        pass

    ### Main entry point for the worker process context

    def main(self, **parameters):

        """ Worker process main method.

            This method is run in the context of the worker process.

            parameters is a dictionary passed in from the control
            script and contains optional parameters for the worker
            process.

        """
        pass

