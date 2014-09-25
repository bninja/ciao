from __future__ import unicode_literals

import logging
import os

import pytest

import ciao


class ResourceError(Exception):

    pass


@pytest.fixture()
def throttle():
    return ciao.Throttle(duration=3, cap=10, exc=(ResourceError,))


@pytest.fixture(scope='session')
def logging_level():
    return {
        'd': logging.DEBUG, 'debug': logging.DEBUG,
        'i': logging.INFO, 'info': logging.INFO,
        'w': logging.WARN, 'warn': logging.WARN,
    }[os.environ.get('SKRILL_TEST_LOG', 'info').lower()]


@pytest.fixture(scope='session', autouse=True)
def logging_config(logging_level):
    logging.basicConfig(level=logging_level)


def test_init():
    with pytest.raises(TypeError):
        ciao.Throttle(duration='nope')
    with pytest.raises(TypeError):
        ciao.Throttle(duration=123, exc=('moops', 'moors'))


def test_backoff():
    throttle = ciao.Throttle(duration=1, cap=10, backoff=2)
    throttle.step()
    throttle.step()
    throttle.step()
    throttle.step()
    throttle.step()
    throttle.step()


def test_step(throttle):
    assert not throttle
    throttle.step()
    assert throttle
    throttle.wait()
    assert not throttle


def test_wait(throttle):
    throttle.wait()


def test_guard(throttle):
    assert not throttle
    with throttle.guard():
        raise ResourceError()
    assert throttle
    throttle.wait()
    assert not throttle
    with throttle.guard():
        pass
    assert not throttle


def test_with(throttle):
    assert not throttle
    with pytest.raises(ResourceError):
        with throttle:
            raise ResourceError()
    assert throttle
    throttle.wait()
    assert not throttle
    with throttle:
        pass
    assert not throttle
