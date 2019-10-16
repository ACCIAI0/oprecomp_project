#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TrainingSession:
    def __init__(self, training_set, test_set, regressor_target_label, classifier_target_label):
        self.__targetRegressor = training_set[regressor_target_label]
        self.__targetClassifier = training_set[classifier_target_label]

        del training_set[regressor_target_label]
        del training_set[classifier_target_label]

        self.__trainingSet = training_set

        self.__testRegressor = test_set[regressor_target_label]
        self.__testClassifier = test_set[classifier_target_label]

        del test_set[regressor_target_label]
        del test_set[classifier_target_label]

        self.__testSet = test_set

    def __len__(self):
        return len(self.training_set)

    @property
    def full_training_data(self):
        copy = self.training_set.copy()
        copy['err_log'] = self.regressor_target.values
        copy['class'] = self.classifier_target.values
        return copy

    @property
    def full_test_data(self):
        copy = self.test_set.copy()
        copy['err_log'] = self.regressor_target_test.values
        copy['class'] = self.classifier_target_test.values
        return copy

    @property
    def training_set(self):
        return self.__trainingSet

    @property
    def test_set(self):
        return self.__testSet

    @property
    def regressor_target(self):
        return self.__targetRegressor

    @property
    def classifier_target(self):
        return self.__targetClassifier

    @property
    def regressor_target_test(self):
        return self.__testRegressor

    @property
    def classifier_target_test(self):
        return self.__testClassifier
