class FeatureBroker:
    def __init__(self, allowReplace=True):
        self.providers = {}
        self.allowReplace = allowReplace

    def Provide(self, feature, provider):
        if not self.allowReplace and provider:
            assert feature not in self.providers, "Duplicate feature: %r" % feature

        if not provider is None:
            self.providers[feature] = provider
        elif feature in self.providers:
            del self.providers[feature]

    def __getitem__(self, feature):
        try:
            provider = self.providers[feature]
        except KeyError:
            raise KeyError("Unknown feature named %r" % feature)

        return provider


def NoAssertion(_):
    return True


def IsInstanceOf(*classes):
    def test(obj):
        return isinstance(obj, classes)

    return test


def HasAttributes(*attributes):
    def test(obj):
        for each in attributes:
            if not hasattr(obj, each):
                return False

        return True

    return test


def HasMethods(*methods):
    def test(obj):
        for each in methods:
            try:
                attr = getattr(obj, each)
            except AttributeError:
                return False
            if not callable(attr):
                return False
        return True

    return test


class RequiredFeature(object):
    def __init__(self, feature, assertion=None, default=None):
        self.feature = feature
        self.assertion = assertion or NoAssertion
        self.default = default

    def __get__(self, obj, T):
        return self.result  # <-- will request the feature upon first call

    def __getattr__(self, name):
        assert name == 'result', "Unexpected attribute request other then 'result'"
        self.result = self.Request()
        return self.result

    def Request(self):
        try:
            obj = features[self.feature]
        except KeyError:
            if self.default:
                obj = self.default
            else:
                raise

        assert self.assertion(obj), \
            "The value %r of %r does not match the specified criteria" \
            % (obj, self.feature)

        return obj


features = FeatureBroker()