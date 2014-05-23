#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging.handlers
from threading import Thread
import config

def smtp_at_your_own_leasure(mailhost, port, username, password, fromaddr, toaddrs, msg, secure, timeout):
    import smtplib
    if not port:
        port = smtplib.SMTP_PORT
    smtp = smtplib.SMTP(mailhost, port, timeout=timeout)
    if username:
        if secure is not None:
            smtp.ehlo()
            smtp.starttls(*secure)
            smtp.ehlo()
        smtp.login(username, password)
    smtp.sendmail(fromaddr, toaddrs, msg.encode("utf-8"))
    smtp.quit()


class ThreadedSMTPHandler(logging.Handler):
    """
    A handler class which sends an SMTP email for each logging event.
    """
    def __init__(self, subject = "povodochek:error"):
        """
        Initialize the handler.

        Initialize the instance with the from and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        """
        logging.Handler.__init__(self)
        mailhost = (config.MAIL_SERVER, 25)
        fromaddr = config.MAIL_USERNAME
        toaddrs = config.ADMIN_EMAILS
        credentials=(config.MAIL_USERNAME, config.MAIL_PASSWORD)
        secure = None
        timeout = 5.0
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self._timeout = timeout

    def getSubject(self, record):
        """
        Determine the subject for the email.

        If you want to specify a subject line which is record-dependent,
        override this method.
        """
        return self.subject

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            from email.utils import formatdate
            port = self.mailport
            
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            
            thread = Thread(target=smtp_at_your_own_leasure, args=(self.mailhost, port, self.username, self.password, self.fromaddr, self.toaddrs, msg, self.secure, self._timeout))
            thread.start()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)