;; (setq debug-on-error t)
(make-directory "/tmp/lovett-emacs" t)
(setq user-emacs-directory "/tmp/lovett-emacs")

(require 'package)
(setq package-archives '(("gnu" . "http://elpa.gnu.org/packages/")
                         ("melpa" . "https://melpa.org/packages/")))
(setq package-user-dir (locate-user-emacs-file "elpa"))
(package-initialize)
(unless (and (package-installed-p 'org)
             (package-installed-p 'ox-rst))
  (package-refresh-contents nil)
  (with-demoted-errors "Error: %S"
    (package-install 'org)
    (package-install 'ox-rst)))

(require 'org-inlinetask)
(require 'ox-publish)
(require 'ox-rst)

(defun lovett-format-inlinetask (_todo todo-type _priority title _tags contents)
  (if (eq todo-type 'done)
      ""
    (format ".. attention:: TODO: %s

%s"
            title
            (if contents
                (replace-regexp-in-string "^" "   " contents)
              ""))))

(defun org-rst-template (contents info)
  "Return complete document string after reStructuredText conversion.
CONTENTS is the transcoded contents string.  INFO is a plist
holding export options."
  (concat
    (concat (org-rst-template--document-title info)
           (let ((depth (plist-get info :with-toc)))
             (when depth "\n.. contents::\n")))
   ;; Added these blank lines to avoid problems
   "\n\n"
   contents
   (and (plist-get info :with-creater)
        (concat
         "\n    :Creator: "
         (plist-get info :creator) "\n"))))

(defun org-rst-special-block (special-block contents info)
  ;; TODO
  (let ((type (downcase (org-element-property :type special-block))))
    (if (string= type "result")
        (format ".. code-block:: none

%s" (replace-regexp-in-string "^" "   " contents))
      contents))
  )

(let ((dir (file-name-directory (or load-file-name
                                    (buffer-file-name))))
      (org-rst-format-inlinetask-function #'lovett-format-inlinetask))
  (org-publish `("lovett-docs"
                 :base-directory ,dir
                 :publishing-directory ,(expand-file-name (concat dir "../build/"))
                 :publishing-function org-rst-publish-to-rst
                 :author "Aaron Ecay"
                 :exclude-tags ("noexport")
                 :section-numbers nil
                 :with-toc nil)
               'force))
