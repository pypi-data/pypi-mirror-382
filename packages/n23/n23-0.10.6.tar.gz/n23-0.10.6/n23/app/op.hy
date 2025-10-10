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

"""
N23 application functions and macros available for N23 application without
an import.
"""

(import contextvars [ContextVar]
        contextlib [AbstractAsyncContextManager]
        n23.app.config [app-config-value]
        n23.sink [sink-from-uri :as n23-sink-from-uri]
        n23.pipeline [fmap])

(require n23.pipeline [n23-> ?-> fmap->])

(setv CTX-CONFIG (ContextVar "CTX_CONFIG"))
(setv CTX-SCHEDULER (ContextVar "CTX_SCHEDULER"))
(setv CTX-PROCESS (ContextVar "CTX_PROCESS"))

(defn set-config [config]
  (CTX-CONFIG.set config))

(defn set-process [managers processes]
  (CTX-PROCESS.set [managers processes]))

(defn set-scheduler [scheduler]
  (CTX-SCHEDULER.set scheduler))

(defn n23-scheduler []
    (CTX-SCHEDULER.get))

(defn n23-config-get [#* args]
  (setv config (CTX-CONFIG.get))
     (app-config-value config #* args))

(defn n23-process [#* args]
  (setv [managers processes] (CTX-PROCESS.get))
  (for [item args]
    (match item
      (AbstractAsyncContextManager) (managers.append item)
      _ (processes.append item))))

(defn n23-add [#* args #** kwargs]
  (setv scheduler (CTX-SCHEDULER.get))
  (scheduler.add #* args #** kwargs))

(export :objects [?->
                  fmap
                  n23-config-get
                  n23-process
                  n23-add
                  n23-sink-from-uri]
        :macros [n23-> fmap-> ?->])

; vim: sw=4:et:ai
