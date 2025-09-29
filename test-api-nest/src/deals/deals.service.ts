import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Deal, DealDocument } from './schemas/deal.schema';

@Injectable()
export class DealsService {
  constructor(
    @InjectModel(Deal.name) private dealModel: Model<DealDocument>,
  ) {}

  async findAll(): Promise<Deal[]> {
    return this.dealModel.find().exec();
  }
}