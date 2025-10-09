#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from abc import abstractmethod
from splashpy.core.framework import Framework


class BaseRouter:

    def __init__(self):
        self.count = 0
        self.success = 0
        pass

    def run(self, inputs, outputs ):
        """Execute All Tasks Received on Request"""
        # Reset Counters
        self.count = 0
        self.success = 0
        # Validate tasks List
        if not self.validate(inputs, outputs):
            return False
        # Init Tasks Results
        outputs['tasks'] = {}
        # Step by Step Execute Tasks
        for index in inputs['tasks']:
            self.count += 1
            outputs['tasks'][index] = self.execute(inputs['tasks'][index])
            if outputs['tasks'][index]['result']:
                self.success += 1

        # Check Global Result
        return self.count == self.success

    @abstractmethod
    def execute(self, task):
        """Execute a Single Task"""
        pass

    @staticmethod
    def validate( inputs, outputs ):

        # Verify Buffers
        if not hasattr(inputs, '__iter__') or not hasattr(outputs, '__iter__'):
            return Framework.log().error('Unable to perform requested action. I/O Buffer not Iterable Type.')

        # Verify Tasks are Defines
        if not 'tasks' in inputs or not hasattr(inputs['tasks'], '__iter__'):
            return Framework.log().warn('Unable to perform requested action, task list is empty.')

        # Verify Tasks are Iterable
        for key in inputs['tasks']:
            if not hasattr(inputs['tasks'][key], '__iter__'):
                return Framework.log().error('Unable to perform requested action. Task is Iterable Type.')

        return True

    @staticmethod
    def empty_response( task ):
        """Build Empty Task Response"""
        return {
            'result': False,
            'data': None,
            'name': task['name'],
            'desc': task['desc'],
        }
