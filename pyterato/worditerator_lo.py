from typing import Tuple, Optional, Any, List

from pyterato.worditerator_base import BaseWordIterator


class LibreOfficeWordIterator(BaseWordIterator):

    def __init__(self, paging=True) -> None:
        super().__init__()

        model, controller = self._initialize_OO()
        self.cursor = model.Text.createTextCursor()
        self.cursor.gotoStart(False)
        self.paging = paging
        if paging:
            self.view_cursor = controller.getViewCursor()

    def _initialize_OO(self) -> Tuple[Any, Any]:
        import uno

        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        ctx = resolver.resolve( "uno:socket,host=localhost,port=8100;urp;StarOffice.ComponentContext" )
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop", ctx)
        model = desktop.getCurrentComponent()
        return model, model.getCurrentController()

    def __iter__(self) -> BaseWordIterator:
        return self

    def __next__(self) -> Tuple[str, Optional[int]]:
        self.cursor.gotoEndOfWord(True)
        if self.paging:
            # FIXME: this line takes most of the time!
            self.view_cursor.gotoRange(self.cursor, False)
            page = self.view_cursor.getPage()
        else:
            page = None

        word = ''.join(e for e in self.cursor.String.lower() if e.isalnum())

        self._prev_words.append(word)
        if not self.cursor.gotoNextWord(False):
            raise StopIteration
        return word, page

    @property
    def prev_words(self) -> List[str]:
        return self._prev_words
