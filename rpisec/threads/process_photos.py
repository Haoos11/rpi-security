# -*- coding: utf-8 -*-

import logging
import time


logger = logging.getLogger()


def process_photos(rpis, camera):
    """
    Monitors the captured_from_camera list for newly captured photos.
    When a new photos are present it will run arp_ping_macs to remove false positives and then send the photos via Telegram.
    After successfully sendind the photo it will also archive the photo and remove it from the list.
    """
    logger.info("thread running")
    while True:
        if not camera.queue.empty():
            if rpis.state.current == 'armed':
                logger.debug('Running arp_ping_macs before sending photos...')
                rpis.arp_ping_macs()
                while True:
                    if rpis.state.current != 'armed':
                        camera.clear_queue()
                        break
                    photo = camera.queue.get()
                    if photo is None:
                        break
                    logger.debug('Processing the photo: {0}'.format(photo))
                    rpis.state.update_triggered(True)
                    rpis.telegram_send_message('Motioned detected')
                    if rpis.telegram_send_file(photo):
                        camera.queue.task_done()
            else:
                logger.debug('Stopping photo processing as state is now {0} and clearing queue'.format(rpis.state.current))
                camera.queue.queue.clear()
        time.sleep(0.1)
