"""
this component serves to provide comment functionality
"""

from py4web import action, URL, request
from yatl.helpers import XML
from py4web.utils.url_signer import URLSigner
from py4web.core import Fixture


class Comment(Fixture):
    COMMENT = """<comment get_url="{get_url}" add_url="{add_url}"
    edit_url="{edit_url}" delete_url="{delete_url}"></comment>"""

    def __init__(self, url, session, signer=None, db=None, auth=None):
        self.get_url = url + '/get'
        self.add_url = url + '/add'
        self.edit_url = url + '/edit'
        self.delete_url = url + '/delete'
        self.signer = signer or URLSigner(session)

        # creates actions (entry points of the calls)
        # same as decorators but registered on object creation
        # very similar to Luca's old component creation
        self.__prerequisites__ = [session]
        args = list(filter(None, [session, db, auth, self.signer.verify()]))

        # function definition
        f = action.uses(*args)(self.get_comments)
        action(self.get_url + "/<id>", method=["GET"])(f)

        f = action.uses(*args)(self.add_comment)
        action(self.add_url, method=["POST"])(f)

        f = action.uses(*args)(self.edit_url)
        action(self.edit_url, method=["POST"])(f)

        f = action.uses(*args)(self.delete_comment)
        action(self.delete_url, method=["POST"])(f)

    def __call__(self, id=None):
        # a clear cut interface is better than dependence on global variables, but including the same user
        # every time might make data strained, adding user as a prop may be added later
        return XML(Comment.COMMENT.format(
            get_url=URL(self.get_url, id, signer=self.signer),
            add_url=URL(self.add_url, signer=self.signer),
            edit_url=URL(self.edit_url, signer=self.signer),
            delete_url=URL(self.delete_url, signer=self.signer)
        ))

    # retrieve all comments associated with this ticket
    def get_comments(self, id=None):
        pass

    # insert a comment associated with this ticket
    # using post because it's way simpler to pass urls this way
    def add_comment(self):
        pass

    # edit a comment associated with this ticket
    # using post for ids
    def edit_comment(self):
        pass

    # delete a comment
    # using post for ids simple
    def delete_comment(self):
        pass
