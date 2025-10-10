;
; n23 - data acquisition and processing framework
;
; Copyright (C) 2013-2023 by Artur Wroblewski <wrobell@riseup.net>
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

(import
  functools [partial]
  funcparserlib.parser [maybe many]
  hy.model-patterns [Symbol Expression Tag keepsym pexpr sym tag whole
                     some
                     STR SYM]

  ...fn [head]
  ...dsl.parser [parse-struct-pos parse-struct-kw parse-struct-kw-named]
  .types [Storage Entity Column])

(defn create-parser [func cls] (partial func cls))

(setv parse-column (create-parser parse-struct-pos Column))
(setv parse-entity (create-parser parse-struct-kw-named Entity))
(setv parse-storage (create-parser parse-struct-kw Storage))

(setv PARSER (whole [
  (>>
    (pexpr
      (keepsym "storage")
      (pexpr (keepsym "version") STR)
      (pexpr (keepsym "role") SYM)
      (maybe (pexpr (keepsym "extensions") (>> (pexpr (many SYM)) head))))
    parse-storage)
  (pexpr
    (keepsym "entities")
    (many (>> (pexpr (sym "entity")
                 SYM
                 (maybe (pexpr (keepsym "partition-by") SYM))
                 (pexpr
                   (keepsym "columns")
                   (many (>> (pexpr
                               SYM
                               (| STR (>> SYM str))
                               (>> (maybe (keepsym "null")) bool))
                             parse-column))))
              parse-entity)))
  (maybe (pexpr (keepsym "sql") STR))
]))

; vim: sw=2:et:ai
