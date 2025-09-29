import { Controller, Get } from '@nestjs/common';
import { LeadsService } from './leads.service';
import { Lead } from './schemas/lead.schema';

@Controller('leads')
export class LeadsController {
  constructor(private readonly leadsService: LeadsService) {}

  @Get()
  async findAll(): Promise<Lead[]> {
    return this.leadsService.findAll();
  }
}