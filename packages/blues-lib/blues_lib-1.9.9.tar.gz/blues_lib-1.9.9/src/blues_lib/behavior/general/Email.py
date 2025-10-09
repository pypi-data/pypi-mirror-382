from blues_lib.util.BluesMailer import BluesMailer
from blues_lib.behavior.Trigger import Trigger

class Email(Trigger):

  def _trigger(self)->bool:
    mailer = BluesMailer.get_instance()
    input_payload = self._config.get('payload')
    payload = self._get_payload(input_payload,mailer)
    stdout = mailer.send(payload)
    return stdout.code == 200

  def _get_payload(self,payload:dict,mailer:BluesMailer)->dict: 
    
    title = payload['content']['title']
    para = payload['content']['para']
    urls = payload['content']['urls']

    return {
      'subject':mailer.get_title_with_time(payload['subject']),
      'content':mailer.get_html_body(title,para,urls),
      'images':payload.get('images'),
      'addressee':payload.get('addressee') or ['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':payload.get('addressee_name') or 'BluesLiu',
    }
