import sqlalchemy
import cProfile
import io
import pstats
import contextlib


def xqp(corpusdb, query_text):
    c = corpusdb.engine.connect()
    return c.execute(sqlalchemy.sql.text("EXPLAIN QUERY PLAN " + query_text)).fetchall()


def xqp_sa(corpusdb, query_obj):
    c = corpusdb.engine.connect()
    return c.execute(sqlalchemy.sql.text("EXPLAIN QUERY PLAN " +
                                         str(query_obj.compile(corpusdb.engine,
                                                               compile_kwargs={"literal_binds": True})))
    ).fetchall()


@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats()
    print (s.getvalue())
