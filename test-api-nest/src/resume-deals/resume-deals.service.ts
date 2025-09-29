import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { TotalDeals, TotalDealsDocument } from './schemas/total-deals.schema';
import {
  ResumeCloseDeals,
  ResumeCloseDealsDocument,
} from './schemas/resume-close-deals.schema';

@Injectable()
export class ResumeDealsService {
  constructor(
    @InjectModel(TotalDeals.name)
    private totalDealsModel: Model<TotalDealsDocument>,
    @InjectModel(ResumeCloseDeals.name)
    private resumeCloseDealsModel: Model<ResumeCloseDealsDocument>,
  ) {}

  async findAllTotalDeals(): Promise<TotalDeals[]> {
    return this.totalDealsModel.find().exec();
  }

  async findAllResumeCloseDeals(): Promise<ResumeCloseDeals[]> {
    return this.resumeCloseDealsModel.find().exec();
  }
}
