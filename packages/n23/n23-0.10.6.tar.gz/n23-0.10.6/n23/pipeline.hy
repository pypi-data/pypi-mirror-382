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
N23 scheduler processes source data with a pipeline function. A function
can be defined with `n23->` macro.

`n23->` macro is based on `some->` macro, and it is designed to

- compose multiple functions to process source data
- short-circuit data processing using function predicates
- split value of N23 scheduler task result into multiple results
- be compatible with other threading (arrow) macros (for example `->>`)

An input and an output of a pipeline function is a N23 task result. Use
`fmap` function or `fmap->` macro to make any function compatible with
a pipeline function.

Use `?->` macro to apply a function predicate and short-circuit data
processing when it returns falsy value.
"""

(import contextvars
        collections [deque]
        dataclasses :as dtc
        functools [cache partial]
        logging

        .fn [identity]
        .scheduler [TaskResult])

(setv logger (logging.getLogger))

(setv CTX-STREAM-MERGE-DEBUG (contextvars.ContextVar "CTX-STREAM-MERGE-DEBUG"))

(defmacro ?-> [result func #* args]
  #[[
  Run filter for a pipeline.

  Return null if the function returns falsy value. It allows to
  short-circuit a pipeline.

  :param result: Value to test, first argument of the filter function.
  :param func: Filter function to run.
  :param args: Remaining arguments of the filter function.
  ]]
  `(let [v ~result] (when (~func v ~@args) v)))

(defmacro n23-> [#* args]
  #[[
  Create function pipeline for N23 scheduler task.

  Pipeline is based on `some->` macro. Therefore it short-circuits when
  a function or macro, part of a pipeline, returns null.
  ]]
  `(fn [result]
     (hy.R.hyrule.some->
       result
       ~@(lfor arg args
           (if (isinstance arg hy.models.List)
             `((fn [result]
                 ~(lfor [idx [name #* se]] (enumerate arg)
                    `(hy.R.hyrule.some->
                       (hy.I.dataclasses.replace result
                                                 :name ~name
                                                 :value (get result.value ~idx))
                       ~@se))))
             arg)))))


(defmacro fmap-> [result func #* args]
  #[[
  Functor macro to process value of a result with a function.

  .. seealso:: `fmap`
  ]]
  `(let [result ~result]
       (setv r (~func result.value ~@args))
       (if (is r None) None (hy.I.dataclasses.replace result :value r))))

(defn [cache] fmap [func]
  #[[
  Create functor for a function.

  ::
    f(T, *args) -> S => f(TaskResult[T], *args) -> TaskResult[S]
    f(T, *args) -> None => f(TaskResult[T], *args) -> None

  If the function returns null, then the functor returs null as well.
  ]]
  (fn [v #* args]
    (setv r (func v.value #* args))
    (if (is r None) None (dtc.replace v :value r))))

(defmacro fn-task-combine [s1 s2 is-left]
  #[[
  Create function to combine values of tasks results of N23 scheduler.

  When a function is called, then (input is N23 scheduler task result)

  - its input is combined with a task result in stream `s2`
  - if the input cannot be combined, then it is added to stream `s1`
  - all task results in stream `s2` are dropped if they cannot be combined
    and have time before time of input task result

  Use `is-left` parameter to keep the same order of values in the combined
  task result, i.e. use false for `(left, right)` and use true for `(right,
  left)` streams merge.
  ]]
  `(fn [name value [delta 0.25]]
     (setv result None)
     (setv combine False)

     ; find matching task result in stream s2
     (while ~s2
       (setv other (. ~s2 (popleft))) ; candidate from stream s2
       ; note: negative value useful during logging to see the relation
       ;       between the input task result and the candidate
       (setv dt (- value.time other.time))
       (cond
         (<= (abs dt) delta) (do (setv combine True)
                                       (break))

         (< value.time other.time) (do (. ~s2 (appendleft other))
                                       (break))
         True (logger.warning
                f"dropping task result: candidate={other}, delta={dt :.2f}")))

     ; when matching task result is found in s2
     (if combine
       (TaskResult (/ (+ value.time other.time) 2.0)
                   name
                   ~(if (hy.eval is-left)
                      `#(other.value value.value)
                      `#(value.value other.value)))
       (. ~s1 (append value)))))

(defn ctor-streams-merge [name [delta 0.25] [buffer-len 16] [debug False]]
  """
  Create functions to merge two streams of task results of N23 scheduler.
  """
  (setv left (deque :maxlen buffer-len))
  (setv right (deque :maxlen buffer-len))
  (when debug
    (CTX-STREAM-MERGE-DEBUG.set [left right]))
  [(partial (fn-task-combine left right False) name :delta delta)
   (partial (fn-task-combine right left True) name :delta delta)])

; vim: sw=2:et:ai
