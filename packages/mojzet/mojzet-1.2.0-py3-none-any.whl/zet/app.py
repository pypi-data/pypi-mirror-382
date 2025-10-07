import asyncio
import textwrap
from aiohttp import ClientSession
from dateutil.parser import parse
from textual import work
from textual.app import App
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Markdown, Static, TabPane, TabbedContent

from zet import api
from zet.entities import News, Route, Stop


class ZetApp(App[None]):
    def __init__(self, session: ClientSession):
        super().__init__()
        self.session = session
        self.animation_level = "none"

    async def on_mount(self):
        self.push_screen(LoadingScreen())
        self.load()

    @work
    async def load(self):
        stops, routes, news = await asyncio.gather(
            api.get_stops(self.session),
            api.get_routes(self.session),
            api.get_newsfeed(self.session),
        )
        self.switch_screen(MainScreen(stops, routes, news))


class MainScreen(Screen):
    def __init__(
        self,
        stops: list[Stop],
        routes: list[Route],
        news: list[News],
    ) -> None:
        super().__init__()
        self.stops = stops
        self.routes = routes
        self.news = news

    def compose(self):
        with TabbedContent():
            yield StopsPane(self.stops)
            yield NewsPane(self.news)


class StopsPane(TabPane):
    DEFAULT_CSS = """
    StopsPane {
        height: auto;

        DataTable {
            height: auto;
        }
    }
    """

    def __init__(self, stops: list[Stop]) -> None:
        super().__init__("Stops")
        self.stops = stops

    def compose(self):
        yield DataTable()

    def on_mount(self):
        dt = self.query_one(DataTable)
        dt.add_columns("ID", "Name", "SearchName")
        for stop in self.stops:
            dt.add_row(
                stop["id"],
                stop["name"],
                stop["normalizedSearchName"],
            )


class NewsPane(TabPane):
    def __init__(self, news: list[News]) -> None:
        super().__init__("News")
        self.news = news

    def compose(self):
        markdown = "\n".join(self._news_generator())
        with VerticalScroll():
            yield Markdown(markdown)

    def _news_generator(self):
        first = True
        for item in self.news:
            if not first:
                yield ""
                yield "---"
                yield ""
            yield f"**{item['title']}**"
            yield ""
            yield item["description"]
            yield ""
            yield item["link"]
            yield ""
            yield parse(item["datePublished"]).strftime("%d.%m.%Y %H:%M")
            first = False


class LoadingScreen(Screen):
    TITLE = "Loading"

    def compose(self):
        yield Header()
        yield Static("Loading...")
        yield Footer()
