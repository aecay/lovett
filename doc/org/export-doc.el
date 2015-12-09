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

(with-eval-after-load 'org-id
  (setq org-id-extra-files (directory-files default-directory t "\\.org\\'")))

(defun lovett-format-block (type headline contents)
  (format ".. %s:: %s

%s"
          type headline
          (replace-regexp-in-string "^" "   " contents)))

(defun lovett-format-inlinetask (todo todo-type _priority title _tags contents)
  (let ((c (or contents ""))
        (tt (or title "")))
    (if (or (eq todo-type 'done) (equal todo ""))
        (lovett-format-block "note" tt c)
      (lovett-format-block "attention" (format "TODO: %s" tt) c))))

(defun org-rst-template (contents info)
  "Return complete document string after reStructuredText conversion.
CONTENTS is the transcoded contents string.  INFO is a plist
holding export options."
  (concat
    (concat (org-rst-template--document-title info)
           (let ((depth (plist-get info :with-toc)))
             (when depth "\n.. contents::\n")))
   ;; AWE: Added these blank lines to avoid problems
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

;;; AWE: removed trailing dummy space
(defun org-rst-subscript (_subscript contents _info)
  "Transcode a SUBSCRIPT object from Org to reStructuredText.
CONTENTS is the contents of the object.  INFO is a plist holding
contextual information."
  (format "\\ :sub:`%s`" contents))
(defun org-rst-superscript (_superscript contents _info)
  "Transcode a SUPERSCRIPT object from Org to reStructuredText.
CONTENTS is the contents of the object.  INFO is a plist holding
contextual information."
  (format "\\ :sup:`%s`" contents))

(defun org-rst-inner-template (contents info)
  "Return complete document string after reStructuredText conversion.
CONTENTS is the transcoded contents string.  INFO is a plist
holding export options."
  (org-element-normalize-string
   (concat
	;; 1. Document's body.
	contents
	;; 2. Footnote definitions.
	(let ((definitions (org-export-collect-footnote-definitions info))
		  ;; Insert full links right inside the footnote definition
		  ;; as they have no chance to be inserted later.
		  (org-rst-links-to-notes nil))
	  (when definitions
		(concat
		 "\n\n"
		 (mapconcat
		  (lambda (ref)
                    (let ((id (format ".. [%s] " (car ref)))
                          ;; AWE: footnote bodies need to be indented
                          (get-fn-body (lambda (x) (replace-regexp-in-string "\n" "\n    "
                                                                             (org-export-data x info)))))
			  ;; Distinguish between inline definitions and
			  ;; full-fledged definitions.
			  (org-trim
			   (let ((def (nth 2 ref)))
				 (if (eq (org-element-type def) 'org-data)
					 ;; Full-fledged definition: footnote ID is
					 ;; inserted inside the first parsed paragraph
					 ;; (FIRST), if any, to be sure filling will
					 ;; take it into consideration.
					 (let ((first (car (org-element-contents def))))
					   (if (not (eq (org-element-type first) 'paragraph))
						   (concat id "\n" (funcall get-fn-body def))
						 (push id (nthcdr 2 first))
						 (funcall get-fn-body def)))
				   ;; Fill paragraph once footnote ID is inserted
				   ;; in order to have a correct length for first
				   ;; line.
				   (concat id (funcall get-fn-body def)))))))
		  definitions "\n\n")))))))

(defun org-rst-headline (headline contents info)
  "Transcode a HEADLINE element from Org to reStructuredText.
CONTENTS holds the contents of the headline.  INFO is a plist
holding contextual information."
  ;; Don't export footnote section, which will be handled at the end
  ;; of the template.
  (unless (org-element-property :footnote-section-p headline)
    (let* (;; Blank lines between headline and its contents.
           ;; `org-rst-headline-spacing', when set, overwrites
           ;; original buffer's spacing.
           (pre-blanks
            (make-string
             (if org-rst-headline-spacing (car org-rst-headline-spacing)
               (org-element-property :pre-blank headline)) ?\n))
           (customid (or (org-element-property :CUSTOM_ID headline)
                         ;; AWE: should also add anchors for the ID
                         (org-element-property :ID headline)))
           (label (when customid
                    (format ".. _%s:\n\n" customid))))
      (concat
       (or label "")
       (org-rst--build-title headline info 'underline)
       "\n" pre-blanks
       contents))))

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
                 :with-toc nil
                 :rst-link-use-ref-role t)
               'force))
