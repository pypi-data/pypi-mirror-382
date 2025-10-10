;
; n23 - data acquisition and processing framework
;
; Copyright (C) 2013-2024 by Artur Wroblewski <wrobell@riseup.net>
;
; This program is free software: you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation, either version 3 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program.  If not, see <http://www.gnu.org/licenses/>.
;

(import asyncio
        contextlib [AsyncExitStack]
        logging
        inspect

        n23.app.op
        .types [ApplicationRunContext ApplicationConfig]
        ..scheduler [Scheduler]
        ..sink [sink-from-uri])

(setv logger (logging.getLogger))

(defn :async run-app [data / [config None]]
  #[[
  Parse and run N23 application.

  Data can be string or Hylang expression defining N23 application.
  ]]
  (when (is config None)
    (setv config (ApplicationConfig [])))
  (match data
    (str) (setv form (hy.read_many data))
    (hy.Expression) (setv form data)
    _ (raise (TypeError "Application data needs to be a string or expression")))

  (await (run-app-ctx (parse-app form config) config)))

(defn parse-app [form config]
  #[[
  Parse N23 application source code and return application run context.

  Form is Hylang expression.
  ]]
  (setv processes [])
  (setv managers [])
  (setv scheduler (Scheduler))
  (n23.app.op.set-config config)
  (n23.app.op.set-process managers processes)
  (n23.app.op.set-scheduler scheduler)

  ; wrap N23 application code with asynchronous coroutine function to allow
  ; top-level `await` calls
  (setv form-task `(defn :async n23-app-setup [] (do ~form)))
  (hy.eval form-task :module n23.app.op)
  (setv n23-app-setup n23.app.op.n23-app-setup)
  (del n23.app.op.n23-app-setup)

  (ApplicationRunContext n23-app-setup scheduler managers processes))

(defn :async run-app-ctx [ctx config]
  #[[
  Run N23 application using N23 application run context.
  ]]
  (setv stack (AsyncExitStack))
  (setv gather asyncio.gather)

  ; setup application and gather processes and process managers to be run
  ; by n23 application framework
  (logger.info "application starting up")
  (await (ctx.setup))

  (logger.info (str.format
                 "application setup run, processes={}, managers={}"
                 (len ctx.processes) (len ctx.process-managers)))

  ; prepare processes and process managers
  (setv processes (ctx.processes.copy))
  (for [cm ctx.process-managers]
    (setv p (await (stack.enter-async-context cm)))
    (when (inspect.isawaitable p)
      (processes.append p)))

  ; run n23 scheduler and application processes and process managers
  (with [:async stack]
    (setv task (gather #* processes ctx.scheduler))
    (await task)))

; vim: sw=2:et:ai
