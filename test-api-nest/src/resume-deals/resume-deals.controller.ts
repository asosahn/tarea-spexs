import { Controller, Get } from '@nestjs/common';
import { ResumeDealsService } from './resume-deals.service';
import { TotalDeals } from './schemas/total-deals.schema';
import { ResumeCloseDeals } from './schemas/resume-close-deals.schema';

@Controller('resume-deals')
export class ResumeDealsController {
  constructor(private readonly resumeDealsService: ResumeDealsService) {}

  @Get('total_deals')
  findAllTotalDeals(): Promise<TotalDeals[]> {
    return this.resumeDealsService.findAllTotalDeals();
  }

  @Get('resume_close_deals')
  findAllResumeCloseDeals(): Promise<ResumeCloseDeals[]> {
    return this.resumeDealsService.findAllResumeCloseDeals();
  }
}
