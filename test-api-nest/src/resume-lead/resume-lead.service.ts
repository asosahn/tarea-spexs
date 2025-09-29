import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { ResumeLead, ResumeLeadDocument } from './schemas/resume-lead.schema';

@Injectable()
export class ResumeLeadService {
  constructor(
    @InjectModel(ResumeLead.name)
    private resumeLeadModel: Model<ResumeLeadDocument>,
  ) {}

  async findAll(): Promise<ResumeLead[]> {
    return this.resumeLeadModel.find().exec();
  }
}
