import logging
from sre_constants import CHARSET
from typing import Union, List, Optional, Iterable, Dict, Any, Sequence
import boto3

from airflow.models import BaseOperator
try:
    from airflow.providers.amazon.aws.hooks.ses import SesHook as ses
except ImportError:
    from airflow.providers.amazon.aws.hooks.ses import SESHook as ses

class DMEmailOperator(BaseOperator):
    """
    Custom email operator
    """
    template_fields: Sequence[str] = ("html_content", "subject")
    template_fields_renderers = { "html_content": "py", "subject": "py"}

    def __init__(
            self,
            *,
            to: Union[List[str], str],
            from_id: str,
            subject: str,
            html_content: str,
            files: Optional[List] = None,
            cc: Optional[Union[List[str], str]] = None,
            bcc: Optional[Union[List[str], str]] = None,
            mime_subtype: str = 'mixed',
            mime_charset: str = 'utf-8',
            conn_id: Optional[str] = "aws_default",
            **kwargs
    ):
        super().__init__(**kwargs)
        self.to = to
        self.from_id = from_id
        self.subject = subject
        self.html_content = html_content
        self.files = files or []
        self.cc = cc
        self.bcc = bcc
        self.mime_subtype = mime_subtype
        self.mime_charset = mime_charset
        self.conn_id = conn_id

    def execute(self, context):
        send_email_ses(
            self.to,
            self.from_id,
            self.subject,
            self.html_content,
            files=self.files,
            cc=self.cc,
            bcc=self.bcc,
            mime_subtype=self.mime_subtype,
            mime_charset=self.mime_charset,
            conn_id=self.conn_id
        )


def send_email_ses(
        to: Union[List[str], Iterable[str]],
        from_id: str,
        subject: str,
        html_content: str,
        files: Optional[List[str]] = None,
        dryrun: bool = False,
        cc: Optional[Union[str, Iterable[str]]] = None,
        bcc: Optional[Union[str, Iterable[str]]] = None,
        mime_subtype: str = 'mixed',
        mime_charset: str = 'utf-8',
        conn_id: Optional[str] = "aws_default",
        custom_headers: Optional[Dict[str, Any]] = None,
        **kwargs ) -> None:
    """Email backend for SES."""
    hook = ses(aws_conn_id=conn_id)

    try:
        response = hook.send_email(
            mail_from=from_id,
            to=to,
            subject=subject,
            html_content=html_content,
            files=files,
            cc=cc,
            bcc=bcc,
            mime_subtype=mime_subtype,
            mime_charset=mime_charset,
        )
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise
