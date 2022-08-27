<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

[pcs\_log](#)

<div class="version">

1.6.118.220826120416

</div>

</div>

<div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="Navigation menu">

  - [Usage](#document-usage)
  - [LogP reference](#document-api)

</div>

</div>

<div class="section wy-nav-content-wrap" data-toggle="wy-nav-shift">

** [pcs\_log](#)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

  - [](#) »
  - pcs\_log 1.6 documentation
  - 

-----

</div>

<div class="document" role="main" itemscope="itemscope" itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="welcome-to-pcs-log-s-documentation" class="section">

# Welcome to pcs\_log’s documentation\!

Document version: 1.6.118.220826120416

<div class="admonition note">

Note

This project is under active development.

</div>

<div id="source" class="section">

## Source

> 
> 
> <div>
> 
> You can get the complete source-code from [GitHub
> repository](https://github.com/rpietsch1953/Log)
> 
> </div>

</div>

<div id="detailed-documentation" class="section">

## Detailed documentation

> 
> 
> <div>
> 
> The detailed documentation is on [Read the
> Docs](https://pcs-log.readthedocs.io/en/latest/index.html)
> 
> </div>

</div>

<div id="table-of-contents" class="section">

## Table of contents

<div class="toctree-wrapper compound">

<span id="document-usage"></span>

<div id="usage" class="section">

### Usage

<div id="installation" class="section">

<span id="id1"></span>

#### Installation

To use pcs\_log, first install it using pip:

<div class="highlight-console notranslate">

<div class="highlight">

    (.venv) $ pip install pcs_log

</div>

</div>

</div>

<div id="use-in-your-program" class="section">

#### Use in your program

  - This module handles the most often used logging options:
    
      - log to console
    
      - log to syslog
    
      - log to file with autorotation
    
      - additional a standalone logging server accessible via telnet
    
      - multiprocessing logs
    
      - mutithreading logs
    
      - enhanced formatting options

normally imported as

<div class="highlight-python notranslate">

<div class="highlight">

    import logging
    from pcs_alog.Logp import LogP

</div>

</div>

</div>

</div>

<span id="document-api"></span>

<div id="logp-reference" class="section">

### LogP reference

<div class="admonition note">

Note

Normally you import only “LogP” from this module.

<div class="highlight-python notranslate">

<div class="highlight">

    import logging
    from pcs_log.LogP import LogP

</div>

</div>

This is a “singleton” and used for all your code-modules. You should
insert this two lines in every module using logging, but call
`SetupLogging()` only once. (except you make your program or parts of it
to “daemons”, in this case you MUST call this function **AFTER**
daemonizing within the daemonized codeblock again, because all the
file-handles are deleted on daemonizing)

</div>

  - *<span class="pre">class</span><span class="w">
    </span>*<span class="sig-prename descclassname"><span class="pre">LogP.</span></span><span class="sig-name descname"><span class="pre">\_LogP</span></span>
    
      - <span class="sig-name descname"><span class="pre">PollRestart</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>
        <span class="sig-return"><span class="sig-return-icon">→</span>
        <span class="sig-return-typehint"><span class="pre">None</span></span></span>  
        Prüfe ob der Logserver neu gestartet werden muss
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">SetupLogging</span></span><span class="sig-paren">(</span>*<span class="o"><span class="pre">\*</span></span>*,
        *<span class="n"><span class="pre">AppName</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">str</span></span>*,
        *<span class="n"><span class="pre">Verbose</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">0</span></span>*,
        *<span class="n"><span class="pre">NoDaemon</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">True</span></span>*,
        *<span class="n"><span class="pre">StdErr</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">StdErrIsStdOut</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">LogPath</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">str</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">''</span></span>*,
        *<span class="n"><span class="pre">LogFileInterval</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">86400</span></span>*,
        *<span class="n"><span class="pre">LogFileCount</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">14</span></span>*,
        *<span class="n"><span class="pre">Quiet</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">LogProcInfo</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">LogProcInfoModLen</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">15</span></span>*,
        *<span class="n"><span class="pre">LogProcInfoFuncLen</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">15</span></span>*,
        *<span class="n"><span class="pre">LogLevelType</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">2</span></span>*,
        *<span class="n"><span class="pre">LogMultiProc</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">LogMultiProcLen</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">15</span></span>*,
        *<span class="n"><span class="pre">LogMultiThread</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">LogMultiThreadLen</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">15</span></span>*,
        *<span class="n"><span class="pre">LogStackOnDebug</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">str</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">'NONE'</span></span>*,
        *<span class="n"><span class="pre">LogLongLevel</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">str</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">'DEBUG'</span></span>*,
        *<span class="n"><span class="pre">LogStackDepth</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">5</span></span>*,
        *<span class="n"><span class="pre">LogDebugIp</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">str</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">'127.0.0.1'</span></span>*,
        *<span class="n"><span class="pre">LogDebugPort</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">0</span></span>*,
        *<span class="n"><span class="pre">LogDebugCacheSize</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">int</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">100</span></span>*,
        *<span class="n"><span class="pre">NoReset</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">False</span></span>*,
        *<span class="n"><span class="pre">TimeOnSyslog</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">bool</span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">True</span></span>*,
        *<span class="n"><span class="pre">translation</span></span><span class="p"><span class="pre">:</span></span><span class="w">
        </span><span class="n"><span class="pre">Optional</span><span class="p"><span class="pre">\[</span></span><span class="pre">dict</span><span class="p"><span class="pre">\]</span></span></span><span class="w">
        </span><span class="o"><span class="pre">=</span></span><span class="w">
        </span><span class="default_value"><span class="pre">None</span></span>*,
        *<span class="o"><span class="pre">\*\*</span></span><span class="n"><span class="pre">kwargs</span></span>*<span class="sig-paren">)</span>
        <span class="sig-return"><span class="sig-return-icon">→</span>
        <span class="sig-return-typehint"><span class="pre">None</span></span></span>
        
        > 
        > 
        > <div>
        > 
        > Creates a defined Log-setting with rich options.
        > 
        > <div class="admonition note">
        > 
        > Note
        > 
        > All arguments are named arguments - NO positional arguments\!
        > 
        > </div>
        > 
        >   - param AppName  
        >     Name of application
        > 
        >   - type AppName  
        >     str
        > 
        >   - param Verbose  
        >     Detail of logging. Defaults to 0. Possible values:
        >     
        >     <div class="highlight-text notranslate">
        >     
        >     <div class="highlight">
        >     
        >         0 = ERROR and STATUS
        >         1 = MSG, WARNING, STATUS, ERROR
        >         2 = INFO, MSG, WARNING, STATUS, ERROR
        >         3 = DEBUG, INFO, MSG, WARNING, STATUS, ERROR
        >         4 = TRACE, DEBUG, INFO, MSG, WARNING, STATUS, ERROR
        >     
        >     </div>
        >     
        >     </div>
        > 
        >   - type Verbose  
        >     int, optional
        > 
        >   - param NoDaemon  
        >     Is this an terminal-task. Defaults to True. If this is
        >     False =\> I am a daemon.
        >     
        >     On deamons output to StdErr do not make any sense, so this
        >     is ignored and “syslog” or “logfile” is used.
        > 
        >   - type NoDaemon  
        >     bool, optional
        > 
        >   - param StdErr  
        >     Log to StdErr. Defaults to False. If this is set the log
        >     goes to StdErr. Ignored if we are a daemon.
        > 
        >   - type StdErr  
        >     bool, optional
        > 
        >   - param StdErrIsStdOut  
        >     Redirect StdErr-Logging to StdOut. Defaults to False.
        > 
        >   - type StdErrIsStdOut  
        >     bool, optional
        > 
        >   - param TimeOnSyslog  
        >     Show timestamp if logging to StdErr. Defaults to True.
        > 
        >   - type TimeOnSyslog  
        >     bool, optional
        > 
        >   - param LogPath  
        >     Log to a Log-file. Defaults to ‘’.
        >     
        >     Log to the file which is given as the argument. this file
        >     is rotated on a daily base and holded up to 14 files
        > 
        >   - type LogPath  
        >     str, optional
        > 
        >   - param LogFileInterval  
        >     Number of seconds a logfile lasts until it is rotated.
        >     Defaults to 60\*60\*24 =\> one day.
        > 
        >   - type LogFileInterval  
        >     int, optional
        > 
        >   - param LogFileCount  
        >     Number of log-file kept. Defaults to 14.
        > 
        >   - type LogFileCount  
        >     int, optional
        > 
        >   - param Quiet  
        >     Output only errors. Defaults to False.
        > 
        >   - type Quiet  
        >     bool, optional
        > 
        >   - param LogProcInfo  
        >     Show process and thread. Defaults to False.
        > 
        >   - type LogProcInfo  
        >     bool, optional
        > 
        >   - param LogLevelType  
        >     Format of LevelInfo. Defaults to 2.
        >     
        >     <div class="highlight-text notranslate">
        >     
        >     <div class="highlight">
        >     
        >         0=None,
        >         1=Number,
        >         2=Name,
        >         3=Both.
        >     
        >     </div>
        >     
        >     </div>
        > 
        >   - type LogLevelType  
        >     int, optional
        > 
        >   - param LogMultiProc  
        >     Show process-names. Defaults to False.
        > 
        >   - type LogMultiProc  
        >     bool, optional
        > 
        >   - param LogMultiThread  
        >     Show thread-names. Defaults to False.
        > 
        >   - type LogMultiThread  
        >     bool, optional
        > 
        >   - param LogProcInfoModLen  
        >     Length of the ‘module’ part of the log. Defaults to 15.
        >     
        >     Set to 0 for not alligning this part. Optimally this is
        >     the length of the longest modulename in your program. This
        >     is only used to allign the log-lines to make the rading
        >     easier. This names are NEVER truncated.
        > 
        >   - type LogProcInfoModLen  
        >     int, optional
        > 
        >   - param LogProcInfoFuncLen  
        >     Length of the ‘function’ part of the log. Defaults to 15.
        >     
        >     Set to 0 for not alligning this part. Optimally this is
        >     the length of the longest functionname in your program.
        >     This is only used to allign the log-lines to make the
        >     rading easier. This names are NEVER truncated.
        > 
        >   - type LogProcInfoFuncLen  
        >     int, optional
        > 
        >   - param LogMultiProcLen  
        >     Length of the ‘procedure’ part of the log. Defaults to 15.
        >     
        >     Set to 0 for not alligning this part. Optimally this is
        >     the length of the longest procedurename in your program.
        >     This is only used to allign the log-lines to make the
        >     rading easier. This names are NEVER truncated.
        > 
        >   - type LogMultiProcLen  
        >     int, optional
        > 
        >   - param LogMultiThreadLen  
        >     Length of the ‘thread’ part of the log. Defaults to 15.
        >     
        >     Set to 0 for not alligning this part. Optimally this is
        >     the length of the longest threadname in your program. This
        >     is only used to allign the log-lines to make the rading
        >     easier. This names are NEVER truncated.
        > 
        >   - type LogMultiThreadLen  
        >     int, optional
        > 
        >   - param LogStackOnDebug  
        >     Log-level below or equal a call-stack trace is included.
        >     
        >     Defaults to “NONE” =\> Disabled. The levels are:
        >     
        >     <div class="highlight-text notranslate">
        >     
        >     <div class="highlight">
        >     
        >         "ERROR"
        >         "STATUS"
        >         "WARNING"
        >         "MSG"
        >         "INFO"
        >         "DEBUG"
        >         "TRACE"
        >         "NONE"
        >     
        >     </div>
        >     
        >     </div>
        >     
        >     All other values are interpretet as “NONE”. Value is not
        >     case-sensitive.
        > 
        >   - type LogStackOnDebug  
        >     str, optional
        > 
        >   - param LogLongLevel  
        >     Log-level below or equal a long info is included.
        >     
        >     Above this level except the ERROR-level the fields
        >     
        >     <div class="highlight-text notranslate">
        >     
        >     <div class="highlight">
        >     
        >         processname,
        >         threadname,
        >         module,
        >         line-no and
        >         levelinfo
        >     
        >     </div>
        >     
        >     </div>
        >     
        >     are not within the output. Alternative this can be a
        >     comma-separated list of levelnames in this case for this
        >     log-levels long infos are provided. Within this list
        >     “NONE” is ignored. Defaults to “DEBUG”.
        >     
        >     The levels are:
        >     
        >     <div class="highlight-text notranslate">
        >     
        >     <div class="highlight">
        >     
        >         "ERROR"
        >         "STATUS"
        >         "WARNING"
        >         "MSG"
        >         "INFO"
        >         "DEBUG"
        >         "TRACE"
        >         "NONE"
        >     
        >     </div>
        >     
        >     </div>
        >     
        >     All other values are interpretet as “NONE”. Value is not
        >     case-sensitive.
        > 
        >   - type LogLongLevel  
        >     str, optional
        > 
        >   - param LogStackDepth  
        >     Maximum number of call-stack entries to display. Defaults
        >     to 5.
        > 
        >   - type LogStackDepth  
        >     int, optional
        > 
        >   - param LogDebugPort  
        >     If 0 no debug-server is started. Else the value has to be
        >     between 1024 and 65535. A log-server is started on
        >     ‘LogDebugIp’ at port ‘LogDebugPort’.
        >     
        >     It is possible to connect to this port (e.g with telnet)
        >     to receive ALL log-messages from this program. ALL means
        >     really all, no mather which loglevel is set. This output
        >     also includes all possible information about process,
        >     thread, module and function. The stacktrace
        >     (‘LogStackOnDebug’) is also honored. This output can be
        >     really heavy, but can help to debug already running
        >     programs without the need to restart with another
        >     loglevel.
        >     
        >     This server runs as a separated process and you have to
        >     terminate it by calling the
        >     [`Stop()`](#LogP._LogP.Stop "LogP._LogP.Stop") function of
        >     the LogP-object, otherwise this process may block the
        >     termination of your program. This server will restart
        >     himselve if it is terminated by any means except you call
        >     the above mentioned functions.
        >     
        >     <div class="admonition note">
        >     
        >     Note
        >     
        >     This port has to be free.
        >     
        >     </div>
        >     
        >     Defaults to 0.
        > 
        >   - type LogDebugPort  
        >     int, optional
        > 
        >   - param LogDebugIp  
        >     The IP-address to bind to. This address must exist on the
        >     host this program is running. ‘0.0.0.0’ for ‘all IPs’ is
        >     also valid. Only examined if ‘LogDebugPort’ \> 0. Defaults
        >     to ‘127.0.0.1’,
        > 
        >   - type LogDebugIp  
        >     str, optional
        > 
        >   - param LogDebugCacheSize  
        >     Only used if ‘LogDebugPort’ \> 0. This is the number of
        >     log-messages cached for use at a new connection to the
        >     server. So if someone connects to the server he receives
        >     the last ‘LogDebugCacheSize’ log messages and after them
        >     all new messages.
        >     
        >     This is like a history. If set to 0 this function is
        >     disabled. Defaults to 100.
        > 
        >   - type LogDebugCacheSize  
        >     int, optional
        > 
        >   - param NoReset  
        >     Do not reset logger on init. Defaults to False.
        >     
        >     <div class="admonition note">
        >     
        >     Note
        >     
        >     Use with care. Could tend to mess up the logging.
        >     
        >     </div>
        > 
        >   - type NoReset  
        >     bool, optional
        > 
        >   - param translation  
        >     If given the programmer can overwrite the error-messages
        >     used. There are 2 functions to help creating this dict:
        >     
        >     > 
        >     > 
        >     > <div>
        >     > 
        >     > LogP.\_PrintInitTranslation()
        >     > LogP.\_PrintActualTranslation()
        >     > 
        >     > </div>
        >     
        >     they do exactly what their name says: they print either
        >     the default value for the translationtable or the actual
        >     value after overwriting some or all values with this dict.
        >     default = {}
        > 
        >   - type translation  
        >     dict, optional
        > 
        > </div>
        
          - After calling this function the new logging is set up. Use
            the standard functions  
            logger.error, logger.warning, etc and additional you can use
            logger.msg, logger.status and logger.trace.
        
          - The severity is in descending order:  
            ERROR, STATUS, WARNING, MSG, INFO, DEBUG, TRACE
        
        At the end of your program call:
        
        > 
        > 
        > <div>
        > 
        > LogP.Stop()
        > 
        > </div>
        
        this will stop the optional logger-process which send the output
        to a telnet-connection if LogDebugPort is not 0.
        
        Output format:
        
        <div class="highlight-text notranslate">
        
        <div class="highlight">
        
            General overview:
                2022-06-22 07:37:42,494 Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Message
                                        ^       ^           ^          ^               ^     ^       ^
                                        |       |           |          |               |     |       |
                Name of application ----+       |           |          |               |     |       |
                    only if not StdErr          |           |          |               |     |       |
                Name of process ----------------+           |          |               |     |       |
                    if LogMultiProc = true                  |          |               |     |       |
                Name of thread if --------------------------+          |               |     |       |
                    LogMultiThread = true                              |               |     |       |
                Module, function and linenumber -----------------------+               |     |       |
                    only if LogProcInfo = true                                         |     |       |
                Level-number of message if LogLevelType = 1 or 3 ----------------------+     |       |
                Level-name of message if LogLevelType = 2 or 3 ------------------------------+       |
                The message given to the log-call ---------------------------------------------------+
            
                The minimal log entry for StdErr is:
                    2022-06-22 07:37:42,494 Errormessage
                The maximal log entry is shown above.
            
            The output format to StdErr is like this:
                2022-06-22 07:37:42,494 MainProcess:MainThread LogP:main:461     - 40=   ERROR - Message
                    No "Appname" because you know whitch program is running.
                    The timestamp is only written if 'TimeOnSyslog' is True.
                    REMEMBER: this is send to StdErr or to StdOut if 'StdErrIsStdOut' is True.
            
            The output format to sylog like this:
                Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Errormessage
                    No timestamp because syslogg adds his own timestamp.
            
            The output format to a logfile is like this:
                2022-06-22 07:37:42,494 Appname:MainProcess:MainThread LogP:main:461 - 40=   ERROR - Message
            
            
            if a call-stack trace is requested lines like these are appended:
                    File "./LogP.py", line 471, in <module>
                    main()
                    File "./LogP.py", line 448, in main
                    abc()
                    File "./LogP.py", line 411, in abc
                    LogP.debug('Debug')
        
        </div>
        
        </div>
    
    <!-- end list -->
    
      - <span class="sig-name descname"><span class="pre">Stop</span></span><span class="sig-paren">(</span><span class="sig-paren">)</span>  
        Stop the Log-Server

</div>

</div>

</div>

</div>

</div>

</div>

-----

<div role="contentinfo">

© Copyright 2022, Ing. Rainer Pietsch.

</div>

Built with [Sphinx](https://www.sphinx-doc.org/) using a
[theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by
[Read the Docs](https://readthedocs.org).

</div>

</div>

</div>

</div>
