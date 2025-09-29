import { Controller, Get } from '@nestjs/common';
import { ResumeLeadService } from './resume-lead.service';
import { ResumeLead } from './schemas/resume-lead.schema';

@Controller('resume-lead')
export class ResumeLeadController {
  constructor(private readonly resumeLeadService: ResumeLeadService) {}

  @Get()
  findAll(): Promise<ResumeLead[]> {
    return this.resumeLeadService.findAll();
  }
}