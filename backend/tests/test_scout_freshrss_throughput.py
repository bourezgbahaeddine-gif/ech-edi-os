from app.agents import scout as scout_module


def test_freshrss_feed_url_adds_nb_limit(monkeypatch) -> None:
    monkeypatch.setattr(scout_module.settings, "freshrss_feed_url", "http://freshrss:80/p/i/?a=rss&state=all")
    monkeypatch.setattr(scout_module.settings, "freshrss_feed_limit", 1000)
    monkeypatch.setattr(scout_module.settings, "scout_max_new_per_run", 800)

    url = scout_module.scout_agent._freshrss_feed_url()

    assert "nb=800" in url
    assert "state=all" in url


def test_freshrss_feed_url_keeps_operator_nb_override(monkeypatch) -> None:
    monkeypatch.setattr(scout_module.settings, "freshrss_feed_url", "http://freshrss:80/p/i/?a=rss&state=all&nb=120")
    monkeypatch.setattr(scout_module.settings, "freshrss_feed_limit", 1000)
    monkeypatch.setattr(scout_module.settings, "scout_max_new_per_run", 800)

    assert scout_module.scout_agent._freshrss_feed_url().endswith("nb=120")
