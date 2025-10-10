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

"""
Parser for N23 application configuration.
"""

(import
  functools [partial]
  funcparserlib.parser [many]
  hy.model-patterns [keepsym pexpr sym whole FORM STR SYM]

  ..dsl.parser [parse-struct-pos]
  .types [ApplicationConfigSection ApplicationConfigItem])

(defn create-parser [func cls] (partial func cls))

(setv parse-config-section (create-parser parse-struct-pos ApplicationConfigSection))
(setv parse-config-item (create-parser parse-struct-pos ApplicationConfigItem))

(setv PARSER (whole [
  (many (>> (pexpr (sym "section") SYM
                   (many (>> (pexpr SYM FORM) parse-config-item)))
            parse-config-section))]))

; vim: sw=2:et:ai
