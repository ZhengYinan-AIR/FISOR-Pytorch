from utils.logger.base_log import BaseLogger
from torch.utils.tensorboard import SummaryWriter

import wandb

class TensorBoardLogger(BaseLogger):
    def __init__(self, project_name, run_name, args, save_path, record_freq: int=100, rank=0):
              super(BaseLogger).__init__()
              """
              project_name (str): wandb project name
              config: dict or argparser
              """              
              self.writer = None

              self.record_freq = record_freq
              
              if rank == 0:
                     if args.wandb:
                            wandb.init(project=project_name, 
                                   name=run_name, 
                                   sync_tensorboard=True, 
                                   reinit=True,  
                                   settings=wandb.Settings(_disable_stats=True))
                            wandb.config.update(args)
                     
                     self.writer = SummaryWriter(log_dir=f'{save_path}/tb')
       

    def log_metrics(self, metrics: dict, step: int):
       """
       metrics (dict):
       step (int, optional): epoch or step
       """
       if self.writer is not None:
              for key, value in metrics.items():
                     self.writer.add_scalar(key, value, step)

    def finish(self):
       if self.writer is not None:
              self.writer.close()
